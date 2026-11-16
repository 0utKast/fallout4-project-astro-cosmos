Scriptname AeroCosmosCarbineEffect extends ActiveMagicEffect

Event OnEffectStart(Actor akTarget, Actor akCaster)
	AeroArmorQuestScript qScript = Game.GetFormFromFile(0x00000804, "AeroArmorMod.esp") as AeroArmorQuestScript
	if qScript != None
		qScript.TriggerCosmicCarbineHit(akTarget, akCaster)
	endif
EndEvent
