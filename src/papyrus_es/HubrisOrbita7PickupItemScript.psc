Scriptname HubrisOrbita7PickupItemScript extends ObjectReference

; =============================================================================
; Componentes de mision (3 Bobinas Fotonicas, Nucleo Sincrotron, Tarjeta Maestra)
; =============================================================================

Event OnContainerChanged(ObjectReference akNewContainer, ObjectReference akOldContainer)
	if akNewContainer != Game.GetPlayer()
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
	if baseObj == Game.GetFormFromFile(0x00001150, "AeroArmorMod.esp")
		ctrl.NotifyQuestItemPickedUp(1)
	elseif baseObj == Game.GetFormFromFile(0x00001151, "AeroArmorMod.esp")
		ctrl.NotifyQuestItemPickedUp(2)
	elseif baseObj == Game.GetFormFromFile(0x00001152, "AeroArmorMod.esp")
		ctrl.NotifyQuestItemPickedUp(3)
	elseif baseObj == Game.GetFormFromFile(0x00001153, "AeroArmorMod.esp")
		ctrl.NotifyQuestItemPickedUp(4)
	elseif baseObj == Game.GetFormFromFile(0x00001154, "AeroArmorMod.esp")
		ctrl.NotifyQuestItemPickedUp(5)
	endif
EndEvent
