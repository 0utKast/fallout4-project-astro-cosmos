Scriptname HubrisOrbita7QuestScript extends Quest

; =============================================================================
; EL LEGADO DE HUBRIS: PROYECTO ASTRO-COSMOS (Estudio Subterraneo Orbita-7)
; Controlador maestro de las 4 misiones encadenadas, examenes con voz del
; Coronel Agallas «Cosmos», desbloqueo progresivo de capsulas y refugio final.
; =============================================================================

int TIMER_RADIO_START = 701
int TIMER_STAGE_POLL  = 702

bool campaignInitialized = false
bool examRunning = false
bool mapFastTravelUnlocked = false
bool arcJetGuardsRefreshedV2 = false
bool fortHagenGuardsRefreshedV2 = false
bool arcJetGuardsRefreshedV3 = false
bool fortHagenGuardsRefreshedV3 = false
int lastStudioCellState = -1
int lastSyncedStage = 0
int activeExamVoiceInst = -1
int activeExamSfxInst = -1
int hitCursor = -1
int failCursor = -1
float activeDiatribeProtectedUntilRT = 0.0
int winCursor1 = -1
int winCursor2 = -1
int winCursor3 = -1
int winCursor4 = -1
int retreatCursor = -1
int pendingCloseBarkType = 0

Actor Property CoronelRef Auto
Actor Property ArtieRef Auto
int Property MIN_CAMPAIGN_LEVEL = 10 AutoReadOnly

Event OnQuestInit()
	RegisterForRemoteEvent(Game.GetPlayer(), "OnPlayerLoadGame")
	RegisterExamTerminals()
	StartTimer(3.5, TIMER_RADIO_START)
EndEvent

Event Actor.OnPlayerLoadGame(Actor akSender)
	examRunning = false
	lastSyncedStage = -1
	lastStudioCellState = -1
	RegisterExamTerminals()
	StartTimer(0.5, TIMER_STAGE_POLL)
EndEvent

Event OnTimer(int aiTimerID)
	if aiTimerID == TIMER_RADIO_START
		Actor player = Game.GetPlayer()
		if GetStage() < 15
			if CanStartOrbita7Campaign(player)
				BeginOrbita7Campaign()
			else
				EnsurePreCampaignSealed()
				StartTimer(4.0, TIMER_RADIO_START)
			endif
			return
		else
			if player == None || !Game.IsMovementControlsEnabled()
				StartTimer(4.0, TIMER_RADIO_START)
				return
			endif
			SyncWorldStateForCurrentStage()
			MigrateExteriorRefsAndObjectives()
			StartTimer(2.0, TIMER_STAGE_POLL)
		endif
	elseif aiTimerID == TIMER_STAGE_POLL
		Actor player = Game.GetPlayer()
		if player == None || !player.Is3DLoaded() || Utility.IsInMenuMode() || !Game.IsMovementControlsEnabled()
			StartTimer(0.5, TIMER_STAGE_POLL)
			return
		endif
		int curStage = GetStage()
		if curStage < 15
			if lastSyncedStage == -1
				AeroArmorQuestScript aeroCtrl = GetAeroController()
				if aeroCtrl != None
					aeroCtrl.EnsureLoadGameBootstrap()
				endif
				lastSyncedStage = curStage
			endif
			if CanStartOrbita7Campaign(player)
				BeginOrbita7Campaign()
			else
				EnsurePreCampaignSealed()
				StartTimer(4.0, TIMER_RADIO_START)
			endif
			return
		endif
		if lastSyncedStage == -1
			AeroArmorQuestScript aeroCtrl = GetAeroController()
			if aeroCtrl != None
				aeroCtrl.EnsureLoadGameBootstrap()
			endif
			SyncWorldStateForCurrentStage()
			MigrateExteriorRefsAndObjectives()
		elseif curStage != lastSyncedStage
			SyncWorldStateForCurrentStage()
		elseif curStage == 15 && !mapFastTravelUnlocked
			UnlockMapMarkerIfVisited(curStage)
		endif
		Cell studioCell = Game.GetFormFromFile(0x00002000, "AeroArmorMod.esp") as Cell
		int nowInStudio = 0
		if studioCell != None && player.GetParentCell() == studioCell
			nowInStudio = 1
		endif
		if lastStudioCellState != -1 && nowInStudio != lastStudioCellState
			EnsureQuestAliasesBound()
			RefreshDisplayedObjectivesSilently()
		endif
		lastStudioCellState = nowInStudio
		if !arcJetGuardsRefreshedV3 || !fortHagenGuardsRefreshedV3
			CheckAndRefreshHostileGuards(curStage)
		endif
		if curStage >= 100
			EnsureCosmosPAPiecesRestored()
		endif
		if curStage > 0 && curStage < 200
			StartTimer(2.0, TIMER_STAGE_POLL)
		endif
	endif
EndEvent

Function EnsureActorRefs()
	if CoronelRef == None
		CoronelRef = Game.GetFormFromFile(0x00002010, "AeroArmorMod.esp") as Actor
	endif
	if ArtieRef == None
		ArtieRef = Game.GetFormFromFile(0x00002011, "AeroArmorMod.esp") as Actor
	endif
EndFunction

ObjectReference Function GetEspRef(int localFormID)
	return Game.GetFormFromFile(localFormID, "AeroArmorMod.esp") as ObjectReference
EndFunction

Function SetRefEnabled(int localFormID, bool shouldEnable)
	ObjectReference r = GetEspRef(localFormID)
	if r != None
		if shouldEnable
			if r.IsDisabled()
				r.Enable()
			endif
		else
			if !r.IsDisabled()
				r.Disable()
			endif
		endif
	endif
EndFunction

AeroArmorQuestScript Function GetAeroController()
	Quest flightQuest = Game.GetFormFromFile(0x00000804, "AeroArmorMod.esp") as Quest
	if flightQuest != None
		return flightQuest as AeroArmorQuestScript
	endif
	return None
EndFunction

bool Function CanStartOrbita7Campaign(Actor player)
	if player == None || !player.Is3DLoaded() || Utility.IsInMenuMode() || !Game.IsMovementControlsEnabled()
		return false
	endif
	if player.GetLevel() < MIN_CAMPAIGN_LEVEL
		return false
	endif
	if player.IsInCombat()
		return false
	endif
	WorldSpace prewarSanctuary = Game.GetFormFromFile(0x000A7FF4, "Fallout4.esm") as WorldSpace
	if prewarSanctuary != None && player.GetWorldSpace() == prewarSanctuary
		return false
	endif
	Location curLoc = player.GetCurrentLocation()
	if curLoc != None
		Location prewarVault111 = Game.GetFormFromFile(0x000CA853, "Fallout4.esm") as Location
		Location vault111Loc = Game.GetFormFromFile(0x0001F3FE, "Fallout4.esm") as Location
		if (prewarVault111 != None && curLoc == prewarVault111) || (vault111Loc != None && curLoc == vault111Loc)
			return false
		endif
	endif
	return true
EndFunction

Function EnsurePreCampaignSealed()
	SetRefEnabled(0x00003005, false)
	SetRefEnabled(0x00003001, false)
	SetRefEnabled(0x00003002, false)
	SetRefEnabled(0x00003003, false)
EndFunction

Function BeginOrbita7Campaign()
	if campaignInitialized
		return
	endif
	campaignInitialized = true
	CancelTimer(TIMER_RADIO_START)

	; Asegurar que los 4 prototipos comienzan custodiados en el Estudio Orbita-7
	AeroArmorQuestScript aeroCtrl = GetAeroController()
	if aeroCtrl != None
		aeroCtrl.ResetPrototypesForCampaignStart()
	endif

	; Activar escotilla exterior en el callejon trasero, baliza y marcador (sin brocal estatico ni viaje rapido aun)
	SetRefEnabled(0x00003005, false) ; Marcador retirado (escotilla a ras de suelo)
	SetRefEnabled(0x00003001, true) ; DoorOrbita7ExteriorHatchRef
	SetRefEnabled(0x00003003, true) ; Luz cian exterior de la escotilla
	ObjectReference mapMarker = GetEspRef(0x00003002)
	if mapMarker != None
		mapMarker.Enable()
		mapMarker.AddToMap(false)
	endif

	SetStage(15)
	SetObjectiveDisplayed(15, true, true)
	SetActive(true)
	lastSyncedStage = 15

	Message radioMsg = Game.GetFormFromFile(0x00001300, "AeroArmorMod.esp") as Message
	if radioMsg != None
		radioMsg.Show()
	endif

	StartTimer(2.0, TIMER_STAGE_POLL)
EndFunction

Function UnlockMapMarkerIfVisited(int stg)
	if mapFastTravelUnlocked
		return
	endif
	bool visited = (stg >= 20)
	if !visited
		Actor player = Game.GetPlayer()
		Cell studioCell = Game.GetFormFromFile(0x00002000, "AeroArmorMod.esp") as Cell
		if player != None && studioCell != None && player.GetParentCell() == studioCell
			visited = true
		endif
	endif
	if visited
		ObjectReference mm = GetEspRef(0x00003002)
		if mm != None
			mm.Enable()
			mm.AddToMap(true)
			mapFastTravelUnlocked = true
		endif
	endif
EndFunction

Function MigrateExteriorRefsAndObjectives()
	if GetStage() < 15
		EnsurePreCampaignSealed()
		return
	endif
	; Garantiza en partidas ya guardadas que el antiguo brocal quede deshabilitado y la escotilla asentada en el callejon trasero
	SetRefEnabled(0x00003005, false)
	SetRefEnabled(0x00003001, true)
	SetRefEnabled(0x00003003, true)

	ObjectReference hatch = GetEspRef(0x00003001)
	if hatch != None && (Math.abs(hatch.GetPositionY() - (-18095.0)) > 5.0 || Math.abs(hatch.GetPositionZ() - 882.5) > 0.5)
		ObjectReference beacon = GetEspRef(0x00003003)
		ObjectReference ftMarker = GetEspRef(0x00003004)
		ObjectReference mapMarker = GetEspRef(0x00003002)

		hatch.SetPosition(7165.0, -18095.0, 882.5)
		hatch.SetAngle(0.0, 0.0, 0.0)
		if beacon != None
			beacon.SetPosition(7165.0, -18095.0, 932.0)
			beacon.SetAngle(0.0, 0.0, 0.0)
		endif
		if ftMarker != None
			ftMarker.SetPosition(7255.0, -18050.0, 885.0)
			ftMarker.SetAngle(0.0, 0.0, -90.0)
		endif
		if mapMarker != None
			mapMarker.SetPosition(7165.0, -18095.0, 940.0)
			mapMarker.SetAngle(0.0, 0.0, 0.0)
		endif
	endif

	; Eleva unicamente los terminales de sobremesa si el jugador esta dentro de Orbita-7 con 3D cargado (sin mover la puerta XNDP)
	Actor player = Game.GetPlayer()
	Cell studioCell = Game.GetFormFromFile(0x00002000, "AeroArmorMod.esp") as Cell
	if player != None && studioCell != None && player.GetParentCell() == studioCell
		ObjectReference termProd = GetEspRef(0x00002057)
		if termProd != None && termProd.Is3DLoaded() && Math.abs(termProd.GetPositionZ() - 1.1) > 0.2
			termProd.SetPosition(termProd.GetPositionX(), termProd.GetPositionY(), 1.1)
		endif
		ObjectReference termArtie = GetEspRef(0x00002059)
		if termArtie != None && termArtie.Is3DLoaded() && Math.abs(termArtie.GetPositionZ() - 1.1) > 0.2
			termArtie.SetPosition(termArtie.GetPositionX(), termArtie.GetPositionY(), 1.1)
		endif
	endif

	; Migrar antigua consola ACTI (0x01002014) hacia la nueva Terminal continua (0x01002018) sobre mesa (0x01002019)
	SetRefEnabled(0x00002014, false)
	SetRefEnabled(0x00002019, true)
	SetRefEnabled(0x00002018, true)
	EnsureQuestAliasesBound()

	; Refresca silenciosamente el objetivo activo para reevaluar QSTA + CTDA exterior/interior
	int curStage = GetStage()
	CheckAndRefreshHostileGuards(curStage)
	if curStage >= 120 && curStage < 140 && !IsObjectiveCompleted(122) && !IsObjectiveDisplayed(122)
		SetObjectiveDisplayed(122, true, false)
	endif
	RefreshDisplayedObjectivesSilently()
EndFunction

Function BindQuestAliasIfEnabled(int aliasIdx, int localFormID)
	ObjectReference targetRef = GetEspRef(localFormID)
	if targetRef != None && !targetRef.IsDisabled()
		ReferenceAlias al = (Self as Quest).GetAlias(aliasIdx) as ReferenceAlias
		if al != None && al.GetReference() != targetRef
			al.ForceRefTo(targetRef)
		endif
	endif
EndFunction

Function EnsureQuestAliasesBound()
	BindQuestAliasIfEnabled(0, 0x00002011)
	BindQuestAliasIfEnabled(1, 0x00002010)
	BindQuestAliasIfEnabled(2, 0x00003001)
	BindQuestAliasIfEnabled(3, 0x00002018)
	BindQuestAliasIfEnabled(4, 0x00002015)
	BindQuestAliasIfEnabled(5, 0x00003010)
	BindQuestAliasIfEnabled(6, 0x00003011)
	BindQuestAliasIfEnabled(7, 0x00003012)
	BindQuestAliasIfEnabled(8, 0x00002016)
	BindQuestAliasIfEnabled(9, 0x00003020)
	BindQuestAliasIfEnabled(10, 0x00002043)
	BindQuestAliasIfEnabled(11, 0x00002013)
	BindQuestAliasIfEnabled(12, 0x00003030)
	BindQuestAliasIfEnabled(13, 0x00002017)
EndFunction

Function RefreshDisplayedObjectivesSilently()
	int curStage = GetStage()
	if curStage <= 0 || curStage >= 200
		return
	endif
	int[] objIds = new int[19]
	objIds[0] = 15
	objIds[1] = 20
	objIds[2] = 30
	objIds[3] = 35
	objIds[4] = 41
	objIds[5] = 42
	objIds[6] = 43
	objIds[7] = 50
	objIds[8] = 60
	objIds[9] = 65
	objIds[10] = 70
	objIds[11] = 80
	objIds[12] = 100
	objIds[13] = 110
	objIds[14] = 121
	objIds[15] = 122
	objIds[16] = 140
	objIds[17] = 160
	objIds[18] = 165
	int idx = 0
	bool refreshed = false
	while idx < objIds.Length
		int oid = objIds[idx]
		if IsObjectiveDisplayed(oid) && !IsObjectiveCompleted(oid)
			SetObjectiveDisplayed(oid, false, false)
			SetObjectiveDisplayed(oid, true, false)
			refreshed = true
		endif
		idx += 1
	endwhile
	if refreshed
		SetActive(true)
	endif
EndFunction

Function SyncWorldStateForCurrentStage()
	EnsureActorRefs()
	int stg = GetStage()

	if stg < 15
		EnsurePreCampaignSealed()
		lastSyncedStage = stg
		return
	endif

	; Escotilla exterior activa a partir de etapa 15; antiguo brocal deshabilitado
	SetRefEnabled(0x00003005, false)
	SetRefEnabled(0x00003001, true)
	SetRefEnabled(0x00003003, true)
	ObjectReference mm = GetEspRef(0x00003002)
	if mm != None && mm.IsDisabled()
		mm.Enable()
		mm.AddToMap(false)
	endif
	UnlockMapMarkerIfVisited(stg)

	; Etapa 20: Inicio Mision 1 (despues de Escena 1 con Artie Vance)
	if stg == 20 && lastSyncedStage < 20
		SetObjectiveCompleted(15, true)
		SetObjectiveDisplayed(20, true, true)
		PlayCoronelBark(1)
	endif

	; Etapa 30: Examen 1 superado -> Cae Barrera #1 (Capsula del Traje)
	if stg >= 30
		SetRefEnabled(0x00002021, false)
	endif
	if stg == 30 && lastSyncedStage < 30
		SetObjectiveCompleted(20, true)
		SetObjectiveDisplayed(30, true, true)
	endif

	; Etapa 35: Traje Astro-Cosmos reclamado -> Hablar con Artie para Mision 2
	if stg == 35 && lastSyncedStage < 35
		SetObjectiveCompleted(30, true)
		SetObjectiveDisplayed(35, true, true)
	endif

	; Etapa 40: Inicio Mision 2 (3 azoteas de Boston)
	if stg >= 40
		SetRefEnabled(0x00003010, true) ; Alijo Azotea Hubris Comics
		SetRefEnabled(0x00003011, true) ; Alijo Terraza Trinity Plaza
		SetRefEnabled(0x00003012, true) ; Alijo Tejado Emisora WRVR
		EnsureQuestAliasesBound()
	endif
	if stg == 40 && lastSyncedStage < 40
		SetObjectiveCompleted(35, true)
		SetObjectiveDisplayed(41, true, true)
		SetObjectiveDisplayed(42, true, false)
		SetObjectiveDisplayed(43, true, false)
		CheckPhotonicCoilsProgress()
	elseif stg >= 40 && stg < 50 && lastSyncedStage == -1
		CheckPhotonicCoilsProgress()
	endif

	; Etapa 50: Las 3 Bobinas Fotonicas reunidas -> Examen 2
	if stg == 50 && lastSyncedStage < 50
		SetObjectiveCompleted(41, true)
		SetObjectiveCompleted(42, true)
		SetObjectiveCompleted(43, true)
		SetObjectiveDisplayed(50, true, true)
	endif

	; Etapa 60: Examen 2 superado -> Cae Barrera #2 (Pedestal de la Carabina)
	if stg >= 60
		SetRefEnabled(0x00002022, false)
	endif
	if stg == 60 && lastSyncedStage < 60
		SetObjectiveCompleted(50, true)
		SetObjectiveDisplayed(60, true, true)
	endif

	; Etapa 65: Carabina Astro-Cosmos reclamada -> Hablar con Artie para Mision 3
	if stg >= 65
		SetRefEnabled(0x00002042, false) ; Ocultar rifle expositor 3D
	endif
	if stg == 65 && lastSyncedStage < 65
		SetObjectiveCompleted(60, true)
		SetObjectiveDisplayed(65, true, true)
	endif

	; Etapa 70: Inicio Mision 3 (Cubierta exterior de ArcJet Systems)
	if stg >= 70
		SetRefEnabled(0x00003020, true) ; Arca Blindada ArcJet
		if lastSyncedStage < 70
			SetRefEnabled(0x00003021, true) ; Centinela ArcJet #1
			SetRefEnabled(0x00003022, true) ; Centinela ArcJet #2
			SetRefEnabled(0x00003023, true) ; Guardian Sincrotron ArcJet
		endif
		EnsureQuestAliasesBound()
	endif
	if stg == 70 && lastSyncedStage < 70
		SetObjectiveCompleted(65, true)
		SetObjectiveDisplayed(70, true, true)
	endif

	; Etapa 80: Nucleo Sincrotron recuperado -> Examen 3
	if stg == 80 && lastSyncedStage < 80
		SetObjectiveCompleted(70, true)
		SetObjectiveDisplayed(80, true, true)
	endif

	; Etapa 100: Examen 3 superado -> Cae Barrera #3 (Hangar Orbital Norte + Servoarmadura Astro-Cosmos)
	if stg >= 100
		SetRefEnabled(0x00002023, false) ; Barrera del Hangar Orbital
		SetRefEnabled(0x00002043, true)  ; Chasis completo Servoarmadura Astro-Cosmos
		EnsureCosmosPAPiecesRestored()
		EnsureQuestAliasesBound()
	endif
	if stg == 100 && lastSyncedStage < 100
		SetObjectiveCompleted(80, true)
		SetObjectiveDisplayed(100, true, true)
	endif

	; Etapa 110: Servoarmadura Astro-Cosmos reclamada -> Hablar con Artie para Mision 4
	if stg == 110 && lastSyncedStage < 110
		SetObjectiveCompleted(100, true)
		SetObjectiveDisplayed(110, true, true)
	endif

	; Etapa 120: Inicio Mision 4 -> Artie abre Sala del Director (Barrera #5) + Activa Boveda Satelital Fort Hagen
	if stg >= 120
		SetRefEnabled(0x00002025, false) ; Barrera de la Sala del Director y Aposentos
		SetRefEnabled(0x00003030, true)  ; Boveda Satelital del Pentagono (Fort Hagen)
		if lastSyncedStage < 120
			SetRefEnabled(0x00003031, true) ; Automata Contratista #1
			SetRefEnabled(0x00003032, true) ; Automata Contratista #2
			SetRefEnabled(0x00003033, true) ; Automata Contratista #3
		endif
		EnsureQuestAliasesBound()
	endif
	if stg == 120 && lastSyncedStage < 120
		SetObjectiveCompleted(110, true)
		SetObjectiveDisplayed(121, true, false)
		SetObjectiveDisplayed(122, true, true)
	endif
	if (stg >= 120 && IsObjectiveCompleted(121)) || stg >= 140
		GlobalVariable gMuralSync = Game.GetFormFromFile(0x00001005, "AeroArmorMod.esp") as GlobalVariable
		if gMuralSync != None && gMuralSync.GetValue() < 1.0
			gMuralSync.SetValue(1.0)
		endif
	endif

	; Etapa 140: Tarjeta Estelar Maestra recuperada -> Examen Maestro #4
	if stg == 140 && lastSyncedStage < 140
		SetObjectiveCompleted(122, true)
		SetObjectiveDisplayed(140, true, true)
	endif

	; Etapa 160: Examen Maestro #4 superado -> Cae Barrera #4 (Relicario Solar del Canon Orbital)
	if stg >= 160
		SetRefEnabled(0x00002024, false)
	endif
	if stg == 160 && lastSyncedStage < 160
		SetObjectiveCompleted(140, true)
		SetObjectiveDisplayed(160, true, true)
	endif

	; Etapa 165: Canon Orbital Gauss reclamado -> Epilogo con Artie Vance
	if stg >= 165
		SetRefEnabled(0x00002044, false) ; Ocultar canon expositor 3D
	endif
	if stg == 165 && lastSyncedStage < 165
		SetObjectiveCompleted(160, true)
		SetObjectiveDisplayed(165, true, true)
	endif

	; Etapa 200: Epilogo completado -> Estudio Orbita-7 desbloqueado como Refugio Permanente
	if stg >= 200 && lastSyncedStage < 200
		SetObjectiveCompleted(121, true)
		SetObjectiveCompleted(165, true)
		GrantFinalStudioOwnership()
	endif

	EnsureQuestAliasesBound()
	lastSyncedStage = stg
EndFunction

Function GrantFinalStudioOwnership()
	Actor player = Game.GetPlayer()
	if player == None
		return
	endif
	Book deed = Game.GetFormFromFile(0x00001163, "AeroArmorMod.esp") as Book
	if deed != None && player.GetItemCount(deed) == 0
		player.AddItem(deed, 1, false)
	endif
	Form caps = Game.GetFormFromFile(0x0000000F, "Fallout4.esm")
	if caps != None
		player.AddItem(caps, 1500, false)
	endif
	Form fCore = Game.GetFormFromFile(0x00075FE4, "Fallout4.esm")
	if fCore != None
		player.AddItem(fCore, 4, false)
	endif
	ObjectReference mm = GetEspRef(0x00003002)
	if mm != None
		mm.AddToMap(true)
	endif
	PlayCoronelBark(18)
	Utility.Wait(1.2)
	Message homeMsg = Game.GetFormFromFile(0x00001324, "AeroArmorMod.esp") as Message
	if homeMsg != None
		homeMsg.Show()
	endif
	CompleteAllObjectives()
	CompleteQuest()
EndFunction

Function PlayCoronelBark(int barkID)
	activeDiatribeProtectedUntilRT = 0.0
	pendingCloseBarkType = 0
	StopActiveExamAudio()
	EnsureActorRefs()
	if CoronelRef == None
		return
	endif
	GlobalVariable gBark = Game.GetFormFromFile(0x00001001, "AeroArmorMod.esp") as GlobalVariable
	Topic tBark = Game.GetFormFromFile(0x00004003, "AeroArmorMod.esp") as Topic
	if gBark != None && tBark != None
		gBark.SetValue(barkID as float)
		CoronelRef.Say(tBark, None, true)
	endif
EndFunction

Function NotifyClueInspected(int clueID)
	; clueID 4 = Gran Mural del Juramento Estelar en la Sala del Director
	if clueID == 4
		GlobalVariable gMural = Game.GetFormFromFile(0x00001005, "AeroArmorMod.esp") as GlobalVariable
		if gMural != None
			gMural.SetValue(1.0)
		endif
		if GetStage() >= 120 && GetStage() < 200
			if IsObjectiveDisplayed(121) && !IsObjectiveCompleted(121)
				SetObjectiveCompleted(121, true)
				Debug.Notification("[Estudio Orbita-7] Juramento Estelar registrado en tu memoria.")
			endif
		endif
	endif
EndFunction

Function NotifyQuestItemPickedUp(int itemKind)
	; 1, 2, 3 = Bobinas Fotonicas (Mision 2)
	; 4 = Nucleo Sincrotron ArcJet (Mision 3)
	; 5 = Tarjeta Estelar Maestra de Clara (Mision 4)
	if itemKind >= 1 && itemKind <= 3
		CheckPhotonicCoilsProgress()
	elseif itemKind == 4
		if GetStage() >= 70 && GetStage() < 80
			SetStage(80)
			SyncWorldStateForCurrentStage()
			Debug.Notification("[Astro-Cosmos] Nucleo Sincrotron recuperado. Lee el expediente y vuelve a Orbita-7.")
		endif
	elseif itemKind == 5
		if GetStage() >= 120 && GetStage() < 140
			SetStage(140)
			SyncWorldStateForCurrentStage()
			Debug.Notification("[Astro-Cosmos] Tarjeta Estelar Maestra recuperada. Escucha la holocinta de Clara y regresa.")
		endif
	endif
EndFunction

Function CheckPhotonicCoilsProgress()
	Actor player = Game.GetPlayer()
	if player == None
		return
	endif
	Form c1 = Game.GetFormFromFile(0x00001150, "AeroArmorMod.esp")
	Form c2 = Game.GetFormFromFile(0x00001151, "AeroArmorMod.esp")
	Form c3 = Game.GetFormFromFile(0x00001152, "AeroArmorMod.esp")
	int count = 0
	if c1 != None && player.GetItemCount(c1) > 0
		count += 1
		if IsObjectiveDisplayed(41) && !IsObjectiveCompleted(41)
			SetObjectiveCompleted(41, true)
		endif
	endif
	if c2 != None && player.GetItemCount(c2) > 0
		count += 1
		if IsObjectiveDisplayed(42) && !IsObjectiveCompleted(42)
			SetObjectiveCompleted(42, true)
		endif
	endif
	if c3 != None && player.GetItemCount(c3) > 0
		count += 1
		if IsObjectiveDisplayed(43) && !IsObjectiveCompleted(43)
			SetObjectiveCompleted(43, true)
		endif
	endif
	GlobalVariable gCoils = Game.GetFormFromFile(0x00001003, "AeroArmorMod.esp") as GlobalVariable
	if gCoils != None
		gCoils.SetValue(count as float)
	endif
	if count >= 3 && GetStage() >= 40 && GetStage() < 50
		SetStage(50)
		SyncWorldStateForCurrentStage()
		Debug.Notification("[Astro-Cosmos] Las 3 Bobinas Fotonicas estan en tu poder. Regresa a Orbita-7.")
	endif
EndFunction

Function NotifyRewardClaimed(int rewardIndex)
	Actor player = Game.GetPlayer()
	if player == None
		return
	endif
	if rewardIndex == 1 && GetStage() >= 30 && GetStage() < 35
		Armor suit = Game.GetFormFromFile(0x00000800, "AeroArmorMod.esp") as Armor
		if suit != None && player.GetItemCount(suit) == 0
			player.AddItem(suit, 1, false)
		endif
		PlayCoronelBark(14)
		SetStage(35)
		SyncWorldStateForCurrentStage()
		Debug.Notification("[Astro-Cosmos] Traje de Vuelo Astro-Cosmos adquirido. Equipalo y pulsa [Y] para volar.")
	elseif rewardIndex == 2 && GetStage() >= 60 && GetStage() < 65
		Weapon carb = Game.GetFormFromFile(0x00000840, "AeroArmorMod.esp") as Weapon
		Form fCells = Game.GetFormFromFile(0x000C1897, "Fallout4.esm")
		if carb != None && player.GetItemCount(carb) == 0
			player.AddItem(carb, 1, false)
		endif
		if fCells != None
			player.AddItem(fCells, 150, false)
		endif
		PlayCoronelBark(15)
		SetStage(65)
		SyncWorldStateForCurrentStage()
		Debug.Notification("[Astro-Cosmos] Carabina de Rayos Astro-Cosmos adquirida (compatible en vuelo con Traje y Servoarmadura).")
	elseif rewardIndex == 3 && GetStage() >= 100 && GetStage() < 110
		EnsureCosmosPAPiecesRestored()
		PlayCoronelBark(16)
		SetStage(110)
		SyncWorldStateForCurrentStage()
		Debug.Notification("[Astro-Cosmos] Servoarmadura Astro-Cosmos reclamada. Habla con Artie Vance.")
	elseif rewardIndex == 4 && GetStage() >= 160 && GetStage() < 165
		Weapon cannon = Game.GetFormFromFile(0x00000850, "AeroArmorMod.esp") as Weapon
		Form ecAmmo = Game.GetFormFromFile(0x0018ABDF, "Fallout4.esm")
		if cannon != None && player.GetItemCount(cannon) == 0
			player.AddItem(cannon, 1, false)
		endif
		if ecAmmo != None
			player.AddItem(ecAmmo, 180, false)
		endif
		PlayCoronelBark(17)
		SetStage(165)
		SyncWorldStateForCurrentStage()
		Debug.Notification("[Astro-Cosmos] Canon Orbital Gauss Astro-Cosmos adquirido (compatible en vuelo con Servoarmadura y Traje).")
	endif
EndFunction

Function ActivateExamConsole()
	SetRefEnabled(0x00002014, false)
	SetRefEnabled(0x00002019, true)
	SetRefEnabled(0x00002018, true)
	ObjectReference termRef = GetEspRef(0x00002018)
	if termRef != None
		ReferenceAlias aliasConsole = (Self as Quest).GetAlias(3) as ReferenceAlias
		if aliasConsole != None && aliasConsole.GetReference() != termRef
			aliasConsole.ForceRefTo(termRef)
		endif
		termRef.Activate(Game.GetPlayer())
	endif
EndFunction

Function RefreshHostileGuardActor(int preplacedRefID, int npcBaseID, ObjectReference anchorRef, float gx, float gy, float gz, float gYaw)
	Actor oldGuard = GetEspRef(preplacedRefID) as Actor
	if oldGuard != None
		if oldGuard.IsDead()
			return
		endif
		oldGuard.DisableNoWait(false)
	endif
	if anchorRef == None
		return
	endif
	ActorBase guardBase = Game.GetFormFromFile(npcBaseID, "AeroArmorMod.esp") as ActorBase
	if guardBase == None
		return
	endif
	ObjectReference spawnedObj = anchorRef.PlaceAtMe(guardBase, 1, false, true, false)
	if spawnedObj != None
		spawnedObj.SetPosition(gx, gy, gz)
		spawnedObj.SetAngle(0.0, 0.0, gYaw)
		spawnedObj.EnableNoWait(false)
		Actor freshActor = spawnedObj as Actor
		if freshActor != None
			freshActor.SetGhost(false)
			freshActor.EvaluatePackage()
		endif
	endif
EndFunction

Function CheckAndRefreshHostileGuards(int curStage)
	if !arcJetGuardsRefreshedV3
		if curStage >= 100
			arcJetGuardsRefreshedV3 = true
		elseif curStage >= 70
			ObjectReference arcJetVault = GetEspRef(0x00003020)
			if arcJetVault != None && arcJetVault.Is3DLoaded()
				arcJetGuardsRefreshedV3 = true
				RefreshHostileGuardActor(0x00003021, 0x00001203, arcJetVault, -68460.0, 18980.0, 4228.0, 0.0)
				RefreshHostileGuardActor(0x00003022, 0x00001203, arcJetVault, -68750.0, 18980.0, 4228.0, 0.0)
				RefreshHostileGuardActor(0x00003023, 0x00001204, arcJetVault, -68608.0, 19280.0, 4228.0, 180.0)
				Debug.Trace("[Orbita-7] Centinelas de ArcJet actualizados con plantilla HandyRace limpia.")
			endif
		endif
	endif

	if !fortHagenGuardsRefreshedV3
		if curStage >= 160
			fortHagenGuardsRefreshedV3 = true
		elseif curStage >= 120
			ObjectReference fhVault = GetEspRef(0x00003030)
			if fhVault != None && fhVault.Is3DLoaded()
				fortHagenGuardsRefreshedV3 = true
				RefreshHostileGuardActor(0x00003031, 0x00001205, fhVault, -86760.0, -5010.0, 6916.0, 0.0)
				RefreshHostileGuardActor(0x00003032, 0x00001205, fhVault, -87060.0, -5010.0, 6916.0, 0.0)
				RefreshHostileGuardActor(0x00003033, 0x00001204, fhVault, -86912.0, -4710.0, 6916.0, 180.0)
				Debug.Trace("[Orbita-7] Automatas de Fort Hagen actualizados con plantilla HandyRace limpia.")
			endif
		endif
	endif
EndFunction

Function EnsureCosmosPAPiecesRestored()
	int stg = GetStage()
	if stg < 100
		return
	endif
	GlobalVariable gRestored = Game.GetFormFromFile(0x00001004, "AeroArmorMod.esp") as GlobalVariable
	if gRestored != None && gRestored.GetValue() >= 1.0
		return
	endif
	Actor player = Game.GetPlayer()
	if player == None || !player.Is3DLoaded() || Utility.IsInMenuMode() || !Game.IsMovementControlsEnabled()
		return
	endif
	ObjectReference paRef = GetEspRef(0x00002043)
	Cell studioCell = Game.GetFormFromFile(0x00002000, "AeroArmorMod.esp") as Cell

	int[] pieceIDs = new int[6]
	pieceIDs[0] = 0x00000820
	pieceIDs[1] = 0x00000821
	pieceIDs[2] = 0x00000822
	pieceIDs[3] = 0x00000823
	pieceIDs[4] = 0x00000824
	pieceIDs[5] = 0x00000825

	bool inPA = player.IsInPowerArmor()
	if stg < 110 && !inPA
		if studioCell == None || player.GetParentCell() != studioCell || paRef == None
			return
		endif
		int addedToChassis = 0
		int i = 0
		while i < pieceIDs.Length
			Form piece = Game.GetFormFromFile(pieceIDs[i], "AeroArmorMod.esp")
			if piece != None
				bool onPlayer = (player.GetItemCount(piece) > 0)
				bool onChassis = (paRef.GetItemCount(piece) > 0)
				if !onPlayer && !onChassis
					paRef.AddItem(piece, 1, true)
					addedToChassis += 1
				endif
			endif
			i += 1
		endwhile
		if addedToChassis > 0 && !paRef.IsDisabled() && paRef.Is3DLoaded()
			paRef.DisableNoWait()
			Utility.Wait(0.15)
			paRef.EnableNoWait()
		endif
	else
		int restoredCount = 0
		int j = 0
		while j < pieceIDs.Length
			Form piece = Game.GetFormFromFile(pieceIDs[j], "AeroArmorMod.esp")
			if piece != None
				bool onPlayer = (player.GetItemCount(piece) > 0)
				bool onChassis = (paRef != None && paRef.GetItemCount(piece) > 0)
				if !onPlayer && !onChassis
					player.AddItem(piece, 1, false)
					restoredCount += 1
					if inPA
						player.EquipItem(piece, false, true)
					endif
				endif
			endif
			j += 1
		endwhile
		if restoredCount > 0
			if inPA
				Debug.Notification("[Astro-Cosmos] Blindaje de la Servoarmadura Astro-Cosmos equipado (" + restoredCount + " piezas).")
			else
				Debug.Notification("[Astro-Cosmos] " + restoredCount + " piezas de la Servoarmadura Astro-Cosmos añadidas a tu inventario.")
			endif
		endif
	endif

	int confirmedCount = 0
	int k = 0
	while k < pieceIDs.Length
		Form piece = Game.GetFormFromFile(pieceIDs[k], "AeroArmorMod.esp")
		if piece != None
			if player.GetItemCount(piece) > 0 || (paRef != None && paRef.GetItemCount(piece) > 0)
				confirmedCount += 1
			endif
		endif
		k += 1
	endwhile

	if gRestored != None && confirmedCount == pieceIDs.Length
		gRestored.SetValue(1.0)
	endif
EndFunction

Function RegisterExamTerminals()
	RegisterForMenuOpenCloseEvent("TerminalMenu")
	int tFid = 0x00001500
	while tFid <= 0x00001514
		Terminal termForm = Game.GetFormFromFile(tFid, "AeroArmorMod.esp") as Terminal
		if termForm != None
			RegisterForRemoteEvent(termForm, "OnMenuItemRun")
		endif
		tFid += 1
	endwhile
EndFunction

int Function PickNextIndex(int prevIdx, int poolSize)
	if poolSize <= 1
		return 0
	endif
	int nextIdx = Utility.RandomInt(0, poolSize - 1)
	if nextIdx == prevIdx
		nextIdx = (prevIdx + 1) % poolSize
	endif
	return nextIdx
EndFunction

int Function PickAndPlayWinVoice(int passedExam)
	int v = 0
	if passedExam == 1
		winCursor1 = PickNextIndex(winCursor1, 3)
		v = winCursor1
	elseif passedExam == 2
		winCursor2 = PickNextIndex(winCursor2, 3)
		v = winCursor2
	elseif passedExam == 3
		winCursor3 = PickNextIndex(winCursor3, 3)
		v = winCursor3
	else
		winCursor4 = PickNextIndex(winCursor4, 3)
		v = winCursor4
	endif
	if v == 0
		return PlayExamSound(0x00001931 + (passedExam - 1))
	endif
	return PlayExamSound(0x00001951 + ((passedExam - 1) * 2) + (v - 1))
EndFunction

int Function PlayExamSound(int localSoundID)
	Sound snd = Game.GetFormFromFile(localSoundID, "AeroArmorMod.esp") as Sound
	if snd == None
		return -1
	endif
	ObjectReference sndSrc = Game.GetPlayer() as ObjectReference
	if sndSrc == None
		EnsureActorRefs()
		sndSrc = CoronelRef
	endif
	if sndSrc == None
		return -1
	endif
	return snd.Play(sndSrc)
EndFunction

Function StopExamSound(int instID)
	if instID != 0 && instID != -1
		Sound.StopInstance(instID)
	endif
EndFunction

Function StopActiveExamAudio()
	StopExamSound(activeExamVoiceInst)
	StopExamSound(activeExamSfxInst)
	activeExamVoiceInst = -1
	activeExamSfxInst = -1
EndFunction

Event OnMenuOpenCloseEvent(string asMenuName, bool abOpening)
	if asMenuName == "TerminalMenu" && !abOpening
		; Si hay una diatriba de victoria/derrota/retirada protegida en reproduccion,
		; no se corta al cerrar el terminal: termina de sonar libremente en 2D.
		pendingCloseBarkType = 0
	endif
EndEvent

Event Terminal.OnMenuItemRun(Terminal akSender, int auiMenuItemID, ObjectReference akTerminalRef)
	float nowRT = Utility.GetCurrentRealTime()
	if auiMenuItemID >= 101 && auiMenuItemID <= 104
		int examNum = auiMenuItemID - 100
		GlobalVariable gExam = Game.GetFormFromFile(0x00001002, "AeroArmorMod.esp") as GlobalVariable
		if gExam != None
			gExam.SetValue(1.0)
		endif
		activeDiatribeProtectedUntilRT = 0.0
		pendingCloseBarkType = 0
		StopActiveExamAudio()
		activeExamVoiceInst = PlayExamSound(0x00001901 + ((examNum - 1) * 3))
	elseif auiMenuItemID >= 105 && auiMenuItemID <= 108
		int retryExamNum = auiMenuItemID - 104
		pendingCloseBarkType = 0
		if nowRT < activeDiatribeProtectedUntilRT && activeExamVoiceInst != -1
			return
		endif
		activeDiatribeProtectedUntilRT = 0.0
		StopActiveExamAudio()
		activeExamVoiceInst = PlayExamSound(0x00001901 + ((retryExamNum - 1) * 3))
	elseif auiMenuItemID == 11 || auiMenuItemID == 12
		activeDiatribeProtectedUntilRT = 0.0
		pendingCloseBarkType = 0
		StopActiveExamAudio()
		hitCursor = PickNextIndex(hitCursor, 12)
		activeExamSfxInst = PlayExamSound(0x00001943 + (hitCursor % 2))
		activeExamVoiceInst = PlayExamSound(0x00001911 + hitCursor)
	elseif auiMenuItemID >= 21 && auiMenuItemID <= 26
		StopActiveExamAudio()
		failCursor = PickNextIndex(failCursor, 16)
		activeExamSfxInst = PlayExamSound(0x00001941 + (failCursor % 2))
		activeExamVoiceInst = PlayExamSound(0x00001921 + failCursor)
		activeDiatribeProtectedUntilRT = nowRT + 9.0
		pendingCloseBarkType = 2
	elseif auiMenuItemID >= 31 && auiMenuItemID <= 34
		int passedExam = auiMenuItemID - 30
		StopActiveExamAudio()
		activeExamSfxInst = PlayExamSound(0x00001944)
		activeExamVoiceInst = PickAndPlayWinVoice(passedExam)
		activeDiatribeProtectedUntilRT = nowRT + 9.5
		pendingCloseBarkType = 1
		AwardExamCompletion(passedExam)
	elseif auiMenuItemID == 90
		if nowRT >= activeDiatribeProtectedUntilRT || activeExamVoiceInst == -1
			StopActiveExamAudio()
			retreatCursor = PickNextIndex(retreatCursor, 4)
			if retreatCursor == 0
				activeExamVoiceInst = PlayExamSound(0x00001935)
			else
				activeExamVoiceInst = PlayExamSound(0x00001960 + retreatCursor)
			endif
			activeDiatribeProtectedUntilRT = nowRT + 6.5
		endif
	elseif auiMenuItemID == 91 || auiMenuItemID == 99
		; Protege las diatribas de fallo/victoria al volver al menu principal o salir
		if nowRT >= activeDiatribeProtectedUntilRT
			activeDiatribeProtectedUntilRT = 0.0
		endif
	endif
EndEvent

Function AwardExamCompletion(int examNum)
	Actor player = Game.GetPlayer()
	if examNum == 1 && GetStage() < 30
		SetStage(30)
	elseif examNum == 2 && GetStage() < 60
		if player != None
			Form c1 = Game.GetFormFromFile(0x00001150, "AeroArmorMod.esp")
			Form c2 = Game.GetFormFromFile(0x00001151, "AeroArmorMod.esp")
			Form c3 = Game.GetFormFromFile(0x00001152, "AeroArmorMod.esp")
			if c1 != None
				player.RemoveItem(c1, 99, true)
			endif
			if c2 != None
				player.RemoveItem(c2, 99, true)
			endif
			if c3 != None
				player.RemoveItem(c3, 99, true)
			endif
		endif
		SetStage(60)
	elseif examNum == 3 && GetStage() < 100
		if player != None
			Form core = Game.GetFormFromFile(0x00001153, "AeroArmorMod.esp")
			if core != None
				player.RemoveItem(core, 99, true)
			endif
		endif
		SetStage(100)
	elseif examNum == 4 && GetStage() < 160
		if player != None
			Form card = Game.GetFormFromFile(0x00001154, "AeroArmorMod.esp")
			if card != None
				player.RemoveItem(card, 99, true)
			endif
		endif
		SetStage(160)
	endif

	GlobalVariable gExam = Game.GetFormFromFile(0x00001002, "AeroArmorMod.esp") as GlobalVariable
	if gExam != None
		gExam.SetValue(0.0)
	endif
	examRunning = false
	SyncWorldStateForCurrentStage()
EndFunction
