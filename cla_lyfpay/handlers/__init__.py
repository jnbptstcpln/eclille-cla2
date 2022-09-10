from .dpr import DancingPartyHandler

HANDLERS = {
    DancingPartyHandler.NAME: DancingPartyHandler
}

def get_handler(origin, event):
    handler = HANDLERS.get(origin)
    if handler and hasattr(handler, event):
        return getattr(handler, event)
    return None