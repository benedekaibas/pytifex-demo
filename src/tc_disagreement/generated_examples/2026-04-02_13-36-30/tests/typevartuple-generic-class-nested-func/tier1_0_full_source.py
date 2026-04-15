from typing import TypeVarTuple, Generic, Callable, reveal_type, Tuple

Ts = TypeVarTuple('Ts')

class ConfigStore[*Ts](Generic[*Ts]): # Generic class with TypeVarTuple
    def __init__(self, *initial_values: *Ts) -> None:
        self.values: Tuple[*Ts] = initial_values

    def get_updater_factory[**P, R](self, key: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
        # Zuban #197 concerns `T` in a closure within a generic class.
        # This takes it further by using `TypeVarTuple` for the class and `ParamSpec`
        # for a factory method that returns a decorator-like callable.
        # The inner `_updater_wrapper` needs to access `self.values` (TypeVarTuple `*Ts`)
        # and correctly handle its own `ParamSpec` and return `R`.
        def updater_decorator(func: Callable[P, R]) -> Callable[P, R]:
            def _updater_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                print(f"Updating key '{key}' from store: {self.values}")
                # Type checkers must track `*Ts` from `self.values` and `P` from the wrapper.
                reveal_type(self.values) # Expect: Tuple[*Ts@ConfigStore]
                reveal_type(args) # Expect: P.args
                return func(*args, **kwargs)
            return _updater_wrapper
        return updater_decorator

if __name__ == "__main__":
    # Create a store with (str, int, bool)
    store = ConfigStore("admin", 123, True)
    reveal_type(store) # Expect: ConfigStore[str, int, bool]

    @store.get_updater_factory("user_status")
    def update_user_status(user_id: int, status: str) -> bool:
        print(f"Setting status '{status}' for user {user_id}")
        return True

    reveal_type(update_user_status) # Expect: Callable[[int, str], bool]
    update_user_status(456, "active")

    # This should be a type error:
    # update_user_status("456", "active") # Uncomment to see expected error