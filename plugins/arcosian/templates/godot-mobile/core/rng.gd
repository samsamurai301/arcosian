extends RefCounted
## Seeded PCG32 (XSH-RR). Deterministic across platforms; state serialises as strings
## because JSON numbers lose precision above 2^53.

const MULT: int = 6364136223846793005

var _state: int = 0
var _inc: int = 0


func _init(seed_value: int = 1, seq: int = 54) -> void:
	_inc = (seq << 1) | 1
	next_u32()
	_state += seed_value
	next_u32()


func next_u32() -> int:
	var old: int = _state
	_state = old * MULT + _inc  # wraps modulo 2^64
	# GDScript >> is arithmetic; mask to emulate the logical shifts of the reference.
	var mixed: int = ((old >> 18) & 0x3FFFFFFFFFFF) ^ old
	var xs: int = (mixed >> 27) & 0xFFFFFFFF
	var rot: int = (old >> 59) & 31
	return ((xs >> rot) | (xs << ((32 - rot) & 31))) & 0xFFFFFFFF


## Uniform-ish integer in [0, n). Modulo bias is below 2^-20 for n <= 4096.
func rand_int(n: int) -> int:
	return next_u32() % n if n > 0 else 0


func rand_float() -> float:
	return float(next_u32()) / 4294967296.0


func to_dict() -> Dictionary:
	return {"state": str(_state), "inc": str(_inc)}


func from_dict(d: Dictionary) -> void:
	_state = String(d.get("state", "0")).to_int()
	_inc = String(d.get("inc", "1")).to_int()
