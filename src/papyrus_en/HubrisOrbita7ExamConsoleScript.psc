Scriptname HubrisOrbita7ExamConsoleScript extends ObjectReference

; =============================================================================
; Redireccion retrocompatible desde el antiguo activador 0x01002014 a la Terminal
; =============================================================================

Event OnActivate(ObjectReference akActionRef)
	if akActionRef != Game.GetPlayer()
		return
	endif
	Self.DisableNoWait()
	ObjectReference tblRef = Game.GetFormFromFile(0x00002019, "AeroArmorMod.esp") as ObjectReference
	if tblRef != None && tblRef.IsDisabled()
		tblRef.Enable()
	endif
	ObjectReference termRef = Game.GetFormFromFile(0x00002018, "AeroArmorMod.esp") as ObjectReference
	if termRef != None
		if termRef.IsDisabled()
			termRef.Enable()
		endif
		Quest q = Game.GetFormFromFile(0x00004000, "AeroArmorMod.esp") as Quest
		if q != None
			ReferenceAlias aliasConsole = q.GetAlias(3) as ReferenceAlias
			if aliasConsole != None
				aliasConsole.ForceRefTo(termRef)
			endif
		endif
		termRef.Activate(akActionRef)
	endif
EndEvent
