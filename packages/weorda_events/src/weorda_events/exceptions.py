class EventDecodeError(ValueError):
    """The envelope bytes cannot be decoded into (event_type, data).

    Per the event-bus contract ack table, the same bytes fail every retry —
    the consumer acks (200) and drops rather than triggering a redelivery
    storm.
    """
