Scriptname HubrisOrbita7CluePlaqueScript extends ObjectReference

; =============================================================================
; Placa / Vitrina / Restirador / Mural interactivo de pistas de Hubris Comics
; =============================================================================

Event OnActivate(ObjectReference akActionRef)
	if akActionRef != Game.GetPlayer()
		return
	endif
	Form baseObj = GetBaseObject()
	Form vit1 = Game.GetFormFromFile(0x00001110, "AeroArmorMod.esp")
	Form vit2 = Game.GetFormFromFile(0x00001111, "AeroArmorMod.esp")
	Form desk = Game.GetFormFromFile(0x00001112, "AeroArmorMod.esp")
	Form mural = Game.GetFormFromFile(0x00001113, "AeroArmorMod.esp")

	int msgFormID = 0x00001301
	int clueID = 1
	if baseObj == vit1
		msgFormID = 0x00001301
		clueID = 1
	elseif baseObj == vit2
		msgFormID = 0x00001302
		clueID = 2
	elseif baseObj == desk
		msgFormID = 0x00001303
		clueID = 3
	elseif baseObj == mural
		msgFormID = 0x00001304
		clueID = 4
	endif

	Message clueMsg = Game.GetFormFromFile(msgFormID, "AeroArmorMod.esp") as Message
	if clueMsg != None
		clueMsg.Show()
	endif

	Quest q = Game.GetFormFromFile(0x00004000, "AeroArmorMod.esp") as Quest
	if q != None
		HubrisOrbita7QuestScript ctrl = q as HubrisOrbita7QuestScript
		if ctrl != None
			ctrl.NotifyClueInspected(clueID)
		endif
	endif
EndEvent
