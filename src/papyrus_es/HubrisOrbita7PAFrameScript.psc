Scriptname HubrisOrbita7PAFrameScript extends ObjectReference

; =============================================================================
; Chasis completo de la Servoarmadura Astro-Cosmos en el Portico del Hangar Norte
; Avanza la Mision 3 (Etapa 100 -> 110) en cuanto el jugador entra o interactua.
; =============================================================================

Event OnActivate(ObjectReference akActionRef)
	if akActionRef == Game.GetPlayer()
		Quest q = Game.GetFormFromFile(0x00004000, "AeroArmorMod.esp") as Quest
		if q != None && q.GetStage() >= 100
			HubrisOrbita7QuestScript ctrl = q as HubrisOrbita7QuestScript
			if ctrl != None
				ctrl.EnsureCosmosPAPiecesRestored()
				if q.GetStage() < 110
					ctrl.NotifyRewardClaimed(3)
				endif
			endif
		endif
	endif
EndEvent
