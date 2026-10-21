extends Node
## IAP interface with a mock store. Real backends (Google Play Billing, StoreKit 2) implement
## purchase(product_id) / restore() and emit purchase_result / restore_done. Always grant on a verified receipt only.

signal purchase_result(product_id: String, success: bool)
signal restore_done(product_ids: Array)

var owned: Array[String] = []
var mock: bool = true
var _backend: Object = null


func set_backend(backend: Object) -> void:
	_backend = backend
	mock = backend == null


func has_product(product_id: String) -> bool:
	return owned.has(product_id)


func purchase(product_id: String) -> void:
	if mock:
		if not owned.has(product_id):
			owned.append(product_id)
		purchase_result.emit.call_deferred(product_id, true)
	else:
		_backend.purchase(product_id)


func restore() -> void:
	if mock:
		restore_done.emit.call_deferred(owned.duplicate())
	else:
		_backend.restore()
