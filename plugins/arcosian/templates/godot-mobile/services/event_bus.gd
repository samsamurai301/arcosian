extends Node
## Global signal hub. Presentation and services talk through this; core never touches it.

signal sim_events(events: Array)
signal game_over(won: bool, score: int)
signal settings_changed
signal app_paused
signal app_resumed
