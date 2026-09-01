extends Area3D

@export var target_group: String = "red_crystal"
@export var popup_message: String = "Achievement: Red Crystal Deposited!"
@export var achievement_name: String = "Red Crystal Master"
@export var notification_label: Label3D
@export var http_request: HTTPRequest

const BACKEND_URL: String = "http://192.168.1.10:8000/add-achievement"

var crystal_deposited: bool = false
var hide_timer: SceneTreeTimer = null
var game_start_time: float = 0.0

# Przechowuje bezpieczny ticket sesji
var session_ticket: String = ""

func _ready() -> void:
	game_start_time = Time.get_ticks_msec() / 1000.0
	body_entered.connect(_on_body_entered)
	if notification_label:
		notification_label.text = ""
		
	# Odczytujemy 'ticket' z paska URL przeglądarki
	if OS.has_feature("web"):
		var js_code = "new URLSearchParams(window.location.search).get('ticket');"
		var url_ticket = JavaScriptBridge.eval(js_code)
		
		if url_ticket != null and str(url_ticket) != "":
			session_ticket = str(url_ticket)
			print("Pobrano ticket sesji w VR: ", session_ticket)

func _on_body_entered(body: Node3D) -> void:
	if crystal_deposited:
		return

	if body.is_in_group(target_group):
		if body.has_method("is_picked_up") and body.is_picked_up():
			body.drop()
			
		crystal_deposited = true
		show_vr_notification(popup_message)
		
		var elapsed_time: float = (Time.get_ticks_msec() / 1000.0) - game_start_time
		trigger_backend_achievement(achievement_name, elapsed_time)
			
		body.queue_free()

func trigger_backend_achievement(ach_name: String, action_time: float) -> void:
	if not http_request:
		print("Brak przypisanego węzła HTTPRequest w Inspectorze!")
		return
		
	var headers = ["Content-Type: application/json"]
	var data = {
		"ticket": session_ticket, # ticket do weryfikacji
		"achievement": ach_name,
		"action_time": action_time
	}
	var json_string = JSON.stringify(data)
	
	var error = http_request.request(BACKEND_URL, headers, HTTPClient.METHOD_POST, json_string)
	if error != OK:
		print("Błąd podczas wysyłania zapytania HTTP z Godota: ", error)

func show_vr_notification(msg: String) -> void:
	if not notification_label:
		return
		
	notification_label.text = msg
	
	if hide_timer and hide_timer.timeout.is_connected(_hide_label):
		hide_timer.timeout.disconnect(_hide_label)
		
	hide_timer = get_tree().create_timer(3.0)
	hide_timer.timeout.connect(_hide_label)

func _hide_label() -> void:
	if notification_label:
		notification_label.text = ""
