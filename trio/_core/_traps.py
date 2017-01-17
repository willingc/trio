# These are the only 3 functions that ever yield back to the task runner.

import types
import enum
from functools import wraps

from . import _hazmat

__all__ = ["yield_briefly", "yield_briefly_no_cancel",
           "Abort", "yield_indefinitely"]

# Decorator to turn a generator into a well-behaved async function:
def asyncfunction(fn):
    # Set the coroutine flag
    fn = types.coroutine(fn)
    # Then wrap it in an 'async def', to enable the "coroutine was not
    # awaited" warning
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        return await fn(*args, **kwargs)
    return wrapper

@_hazmat
@asyncfunction
def yield_briefly():
    return (yield (yield_briefly,))

@_hazmat
@asyncfunction
def yield_briefly_no_cancel():
    return (yield (yield_briefly_no_cancel,))

# Return values for abort functions
@_hazmat
class Abort(enum.Enum):
    SUCCEEDED = 1
    FAILED = 2

# This is a very finicky interface. ParkingLot provides a much more pleasant
# abstraction on top of it.
#
# Basically, before calling this make arrangements for the current task to be
# rescheduled "eventually".
#
# abort_func gets called if we want to cancel the wait (e.g. a
# timeout). It should attempt to cancel whatever arrangements were made, and
# must return either Interupt.SUCCEEDED, in which case the task will be
# rescheduled immediately with the exception raised, or else Abort.FAILED,
# in which case no magic happens and you still have to make sure that
# reschedule will be called eventually.
@_hazmat
@asyncfunction
def yield_indefinitely(abort_func):
    return (yield (yield_indefinitely, abort_func))