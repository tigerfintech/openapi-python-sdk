class Context:
    def __init__(self):
        self.account = None
        self.asset_manager = None
        self.position_manager = None
        self.order_manager = None
        self.active_order_manager = None
        self.contract_map = {}


global_context = Context()