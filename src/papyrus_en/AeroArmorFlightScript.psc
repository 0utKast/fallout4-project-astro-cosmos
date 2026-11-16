Scriptname AeroArmorFlightScript extends ActiveMagicEffect

; El control de vuelo ahora reside de forma permanente en AeroArmorQuestScript
; para que funcione con cualquier armadura o Servoarmadura de la Hermandad sin desactivarse.

Event OnEffectStart(Actor akTarget, Actor akCaster)
	if akTarget == Game.GetPlayer()
		Quest flightQuest = Game.GetFormFromFile(0x00000804, "AeroArmorMod.esp") as Quest
		if flightQuest != None
			AeroArmorQuestScript aeroCtrl = flightQuest as AeroArmorQuestScript
			if aeroCtrl != None && aeroCtrl.PlayerRef == None
				aeroCtrl.EnsureLoadGameBootstrap()
			endif
		endif
	endif
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
EndEvent
