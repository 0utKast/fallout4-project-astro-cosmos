Scriptname HubrisOrbita7RewardPodScript extends ObjectReference

; =============================================================================
; Capsula / Pedestal Fotonico / Relicario Solar de recompensas Astro-Cosmos
; =============================================================================

Event OnActivate(ObjectReference akActionRef)
	if akActionRef != Game.GetPlayer()
		return
	endif
	Quest q = Game.GetFormFromFile(0x00004000, "AeroArmorMod.esp") as Quest
	if q == None
		return
	endif
	HubrisOrbita7QuestScript ctrl = q as HubrisOrbita7QuestScript
	if ctrl == None
		return
	endif

	Form baseObj = GetBaseObject()
	Form podSuit = Game.GetFormFromFile(0x00001115, "AeroArmorMod.esp")
	Form pedWeap = Game.GetFormFromFile(0x00001116, "AeroArmorMod.esp")
	Form relSolar = Game.GetFormFromFile(0x00001117, "AeroArmorMod.esp")

	int stg = q.GetStage()
	if baseObj == podSuit
		if stg >= 30 && stg < 35
			ctrl.NotifyRewardClaimed(1)
		elseif stg >= 35
			Debug.Notification("[Estudio Orbita-7] Ya has reclamado el Traje de Vuelo Astro-Cosmos.")
		else
			Debug.Notification("[Estudio Orbita-7] Capsula sellada. Supera el Examen de Recluta del Coronel Agallas.")
		endif
	elseif baseObj == pedWeap
		if stg >= 60 && stg < 65
			ctrl.NotifyRewardClaimed(2)
		elseif stg >= 65
			Debug.Notification("[Estudio Orbita-7] Ya has reclamado la Carabina de Rayos Astro-Cosmos.")
		else
			Debug.Notification("[Estudio Orbita-7] Pedestal sellado. Supera el Examen de Patrulla Aerea.")
		endif
	elseif baseObj == relSolar
		if stg >= 160 && stg < 165
			ctrl.NotifyRewardClaimed(4)
		elseif stg >= 165
			Debug.Notification("[Estudio Orbita-7] Ya has reclamado el Canon Orbital Gauss Astro-Cosmos.")
		else
			Debug.Notification("[Estudio Orbita-7] Relicario sellado. Supera el Examen Maestro Capitan del Cosmos.")
		endif
	endif
EndEvent
