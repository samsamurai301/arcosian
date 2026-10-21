extends Node
## Mobile lifecycle: autosave when the app is paused, loses focus or is asked to close.

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func _notification(what: int) -> void:
	match what:
		NOTIFICATION_APPLICATION_PAUSED, NOTIFICATION_APPLICATION_FOCUS_OUT, NOTIFICATION_WM_WINDOW_FOCUS_OUT:
			EventBus.app_paused.emit()
			SaveService.mark_dirty()
			SaveService.flush()
		NOTIFICATION_APPLICATION_RESUMED, NOTIFICATION_APPLICATION_FOCUS_IN, NOTIFICATION_WM_WINDOW_FOCUS_IN:
			EventBus.app_resumed.emit()
		NOTIFICATION_WM_CLOSE_REQUEST:
			EventBus.app_paused.emit()
			SaveService.mark_dirty()
			SaveService.flush()
