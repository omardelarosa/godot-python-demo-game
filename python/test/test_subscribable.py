
from python.lib.subscribable import Subscribable

def test_game_manager_setup():
    s = Subscribable()

    arr = []

    def f(x):
        arr.append(x)

    event_signal_key = 'add_one'

    # test adding a subscription
    s.subscribe({ (event_signal_key): [f] })

    # send two test events to mutate the array
    s.send(event_signal_key, 1)
    s.send(event_signal_key, 2)

    # ensure that array got both values
    assert arr == [1, 2]

    # test removing a subscription
    s.unsubscribe({ (event_signal_key): [f] })

    # send a third event to mutate the array
    s.send(event_signal_key, 3)

    # ensure that event did not get called again
    assert arr == [1, 2]