from _typeshed import Incomplete
from ctypes import Structure, Union, byref as byref, c_wchar_p as c_wchar_p

def cfunc(name, dll, result, *args): ...

dll: Incomplete
EVENT_LIST_TERMINATED: int
EVENT_WORD: int
EVENT_SENTENCE: int
EVENT_MARK: int
EVENT_PLAY: int
EVENT_END: int
EVENT_MSG_TERMINATED: int

class numberORname(Union): ...
class EVENT(Structure): ...

AUDIO_OUTPUT_PLAYBACK: int
AUDIO_OUTPUT_RETRIEVAL: int
AUDIO_OUTPUT_SYNCHRONOUS: int
AUDIO_OUTPUT_SYNCH_PLAYBACK: int
EE_OK: int
EE_INTERNAL_ERROR: int
EE_BUFFER_FULL: int
EE_NOT_FOUND: int
Initialize: Incomplete
t_espeak_callback: Incomplete
cSetSynthCallback: Incomplete
SynthCallback: Incomplete

def SetSynthCallback(cb) -> None: ...

t_UriCallback: Incomplete
cSetUriCallback: Incomplete
UriCallback: Incomplete

def SetUriCallback(cb) -> None: ...

CHARS_AUTO: int
CHARS_UTF8: int
CHARS_8BIT: int
CHARS_WCHAR: int
SSML: int
PHONEMES: int
ENDPAUSE: int
KEEP_NAMEDATA: int
POS_CHARACTER: int
POS_WORD: int
POS_SENTENCE: int

def Synth(text, position: int = ..., position_type=..., end_position: int = ..., flags: int = ..., user_data: Incomplete | None = ...): ...

cSynth: Incomplete

def Synth_Mark(text, index_mark, end_position: int = ..., flags=...) -> None: ...

cSynth_Mark: Incomplete
Key: Incomplete
Char: Incomplete
SILENCE: int
RATE: int
VOLUME: int
PITCH: int
RANGE: int
PUNCTUATION: int
CAPITALS: int
EMPHASIS: int
LINELENGTH: int
PUNCT_NONE: int
PUNCT_ALL: int
PUNCT_SOME: int
SetParameter: Incomplete
GetParameter: Incomplete
SetPunctuationList: Incomplete
SetPhonemeTrace: Incomplete
CompileDictionary: Incomplete

class VOICE(Structure): ...

cListVoices: Incomplete

def ListVoices(voice_spec: Incomplete | None = ...): ...

SetVoiceByName: Incomplete
SetVoiceByProperties: Incomplete
GetCurrentVoice: Incomplete
Cancel: Incomplete
IsPlaying: Incomplete
Synchronize: Incomplete
Terminate: Incomplete
Info: Incomplete
