from inspect import iscoroutinefunction
from typing import Any, Callable, Dict, Optional

from graphql import (
    GraphQLArgument,
    GraphQLField,
    GraphQLFieldMap,
    GraphQLInputField,
    GraphQLInputFieldMap,
    GraphQLInputObjectType,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLResolveInfo,
    GraphQLString,
    Thunk,
)
from graphql.pyutils import AwaitableOrValue

# Note: Contrary to the Javascript implementation of MutationFn,
# the context is passed as part of the GraphQLResolveInfo and any arguments
# are passed individually as keyword arguments.
MutationFnWithoutArgs = Callable[[GraphQLResolveInfo], AwaitableOrValue[Any]]
# Unfortunately there is currently no syntax to indicate optional or keyword
# arguments in Python, so we also allow any other Callable as a workaround:
MutationFn = Callable[..., AwaitableOrValue[Any]]


def resolve_maybe_thunk(thing_or_thunk: Thunk) -> Any:
    return thing_or_thunk() if callable(thing_or_thunk) else thing_or_thunk


class NullResult:
    def __init__(self, clientMutationId: Optional[str] = None) -> None:
        self.clientMutationId = clientMutationId


def mutation_with_client_mutation_id(
    name: str,
    input_fields: Thunk[GraphQLInputFieldMap],
    output_fields: Thunk[GraphQLFieldMap],
    mutate_and_get_payload: MutationFn,
    description: Optional[str] = None,
    deprecation_reason: Optional[str] = None,
    extensions: Optional[Dict[str, Any]] = None,
) -> GraphQLField:
    """
    Returns a GraphQLFieldConfig for the specified mutation.

    The input_fields and output_fields should not include `clientMutationId`,
    as this will be provided automatically.

    An input object will be created containing the input fields, and an
    object will be created containing the output fields.

    mutate_and_get_payload will receive a GraphQLResolveInfo as first argument,
    and the input fields as keyword arguments, and it should return an object
    (or a dict) with an attribute (or a key) for each output field.
    It may return synchronously or asynchronously.
    """

    def augmented_input_fields() -> GraphQLInputFieldMap:
        return dict(
            resolve_maybe_thunk(input_fields),
            clientMutationId=GraphQLInputField(GraphQLString),
        )

    def augmented_output_fields() -> GraphQLFieldMap:
        return dict(
            resolve_maybe_thunk(output_fields),
            clientMutationId=GraphQLField(GraphQLString),
        )

    output_type = GraphQLObjectType(name + "Payload", fields=augmented_output_fields)

    input_type = GraphQLInputObjectType(name + "Input", fields=augmented_input_fields)

    if iscoroutinefunction(mutate_and_get_payload):

        # noinspection PyShadowingBuiltins
        async def resolve(_root: Any, info: GraphQLResolveInfo, input: Dict) -> Any:
            payload = await mutate_and_get_payload(info, **input)
            clientMutationId = input.get("clientMutationId")
            if payload is None:
                return NullResult(clientMutationId)
            payload.clientMutationId = clientMutationId
            return payload

    else:

        # noinspection PyShadowingBuiltins
        def resolve(  # type: ignore
            _root: Any, info: GraphQLResolveInfo, input: Dict
        ) -> Any:
            payload = mutate_and_get_payload(info, **input)
            clientMutationId = input.get("clientMutationId")
            if payload is None:
                return NullResult(clientMutationId)
            payload.clientMutationId = clientMutationId  # type: ignore
            return payload

    return GraphQLField(
        output_type,
        description=description,
        deprecation_reason=deprecation_reason,
        args={"input": GraphQLArgument(GraphQLNonNull(input_type))},
        resolve=resolve,
        extensions=extensions,
    )
