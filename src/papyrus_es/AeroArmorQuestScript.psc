Scriptname AeroArmorQuestScript extends Quest

Actor Property PlayerRef Auto Hidden
Perk Property NoFallDamagePerk Auto Hidden
Perk Property CosmicRadShieldPerk Auto Hidden
Spell Property CustomFlightSpell Auto Hidden
ActorValue Property PABatteryDamageRateAV Auto Hidden
ActorValue Property ActionPointsAV Auto Hidden
Form Property HoverPlatformForm Auto Hidden
Keyword Property NoImpactLandKeyword Auto Hidden
SoundCategory Property PlayerFootstepCat Auto Hidden
SoundCategory Property PlayerFootstepSubCat Auto Hidden
Armor Property HeroFlightSuit Auto Hidden
Armor Property CosmosPATorso Auto Hidden
Keyword Property CosmosPATorsoKw Auto Hidden
Weapon Property CosmosHeroCarbine Auto Hidden
Keyword Property CosmosHeroWeapKw Auto Hidden
Weapon Property CosmosPACannon Auto Hidden
Keyword Property CosmosPAWeapKw Auto Hidden

Perk powerArmorPerkCached = None
ObjectReference platA = None
ObjectReference platB = None

bool isFloating = false
bool isAscending = false
bool isDescending = false
bool justStartedDescent = false
bool justStoppedDescent = false
bool jumpHeld = false
bool platEnabled = false
bool isPrewarming = false
bool isTimerTicking = false
bool brakePulse = false
bool has3rdPersonFlavor = false
bool pending3rdPersonCleanup = false
bool pendingGroundFlavorReset = false
bool footstepsMuted = false
bool inPowerArmorCached = false
bool hasHeroSuitEquipped = false
bool hasCosmosPATorsoEquipped = false
bool hasHeroWeapEquipped = false
bool hasPAWeapEquipped = false
bool starterSuitGranted = false
bool starterPAGranted = false
bool starterHeroWeapGranted = false
bool starterPAWeapGranted = false
bool forceAuxCheck = false
bool sprintBoostActive = false
bool hasFallenDuringDescent = false
bool povTogglePending = false
bool aimHeld = false
bool scopeMenuOpen = false
bool pipboyMenuOpen = false
bool pendingPostPipboySync = false
bool aimBackOffsetActive = false
bool readyWeaponHeld = false

float lockedZ = 0.0
float lastZ = 0.0
float takeoffZ = 0.0
float takeoffRealTime = 0.0
float lastAimReleaseTime = 0.0
float lastPipboyCloseTime = 0.0
float lastPlatX = 0.0
float lastPlatY = 0.0
float lastRelayPlayerX = 0.0
float lastRelayPlayerY = 0.0
float lastPlayerX = 0.0
float lastPlayerY = 0.0
float readyWeaponDownTime = 0.0
float lastHolsterStartTime = 0.0
float lastLoadBootstrapRealTime = 0.0

int climbTicks = 0
int landedTicks = 0
int syncStep = 0
int active3rdPersonFlavorMode = 0
int activePlat = 0
int auxCheckCounter = 0
int cellCheckCounter = 0
int flightSessionId = 0
int landCleanTicks = 0
int landSwitchFollowups = 0
int cosmicHitCounter = 0
int solarCannonHitCounter = 0

int Property KEY_H = 35 AutoReadOnly

int Property TIMER_INIT = 201 AutoReadOnly
int Property TIMER_FLOAT = 202 AutoReadOnly
int Property TIMER_POV_CLEAN = 203 AutoReadOnly
int Property TIMER_LAND_CLEAN = 204 AutoReadOnly
int Property TIMER_POST_PIPBOY = 205 AutoReadOnly

Event OnInit()
	SetupFlightSystem(true)
EndEvent

Function ResetLoadTransientState()
	; Reinicia estado transitorio de vuelo tras cargar partida (OnPlayerLoadGame o recuperacion tras ReloadScript).
	PlayerRef = Game.GetPlayer()
	lastLoadBootstrapRealTime = Utility.GetCurrentRealTime()
	flightSessionId += 1
	isFloating = false
	isAscending = false
	isDescending = false
	hasFallenDuringDescent = false
	sprintBoostActive = false
	forceAuxCheck = false
	isPrewarming = false
	isTimerTicking = false
	povTogglePending = false
	aimHeld = false
	scopeMenuOpen = false
	pipboyMenuOpen = false
	pendingPostPipboySync = false
	justStartedDescent = false
	justStoppedDescent = false
	jumpHeld = false
	brakePulse = false
	climbTicks = 0
	landedTicks = 0
	auxCheckCounter = 0
	lastAimReleaseTime = 0.0
	lastPipboyCloseTime = 0.0
	readyWeaponHeld = false
	readyWeaponDownTime = 0.0
	lastHolsterStartTime = 0.0
	CancelTimer(TIMER_FLOAT)
	CancelTimer(TIMER_LAND_CLEAN)
	CancelTimer(TIMER_POV_CLEAN)
	CancelTimer(TIMER_POST_PIPBOY)
	SetFlightFootstepsMuted(false)
	if has3rdPersonFlavor || syncStep != 0
		pendingGroundFlavorReset = true
	endif
EndFunction

Event Actor.OnPlayerLoadGame(Actor akSender)
	ResetLoadTransientState()
	StartTimer(2.0, TIMER_INIT)
EndEvent

Function EnsureLoadGameBootstrap()
	; Recupera registros de controles y eventos tras cargas afectadas por ReloadScript (PlayerRef = None).
	float now = Utility.GetCurrentRealTime()
	if PlayerRef != None && lastLoadBootstrapRealTime > 0.0 && now >= lastLoadBootstrapRealTime && (now - lastLoadBootstrapRealTime) < 30.0
		return
	endif
	Debug.Trace("[Aero-Mod] EnsureLoadGameBootstrap: recuperando registros de vuelo tras carga o ReloadScript.")
	ResetLoadTransientState()
	if PlayerRef != None
		RegisterForRemoteEvent(PlayerRef, "OnPlayerLoadGame")
	endif
	StartTimer(0.25, TIMER_INIT)
EndFunction

Event Actor.OnItemEquipped(Actor akSender, Form akBaseObject, ObjectReference akReference)
	bool wasSuit = hasHeroSuitEquipped
	bool wasPATorso = hasCosmosPATorsoEquipped
	bool wasHeroWeap = hasHeroWeapEquipped
	bool wasPAWeap = hasPAWeapEquipped
	RefreshPowerArmorCache()
	RefreshHeroSuitCache()
	RefreshCosmosPACache()
	RefreshHeroWeaponCache()
	RefreshPAWeaponCache()
	forceAuxCheck = true
	if !PlayerRef || !PlayerRef.Is3DLoaded() || IsPipboyOrMenuBusy()
		; Nunca mutar keywords/perks/animaciones del jugador mientras el 3D no este cargado o el Pip-Boy (Quick-Boy PA)
		; este abierto o cerrandose, para no bloquear el evento pipboyClosed ni provocar cierres en cargas de partida.
		pendingPostPipboySync = true
		if !PlayerRef || !PlayerRef.Is3DLoaded()
			StartTimer(0.50, TIMER_POST_PIPBOY)
		endif
		return
	endif
	EnsureFlightAbilities()
	if (isFloating || isAscending) && ((!wasHeroWeap && hasHeroWeapEquipped) || (!wasPAWeap && hasPAWeapEquipped)) && !PlayerRef.GetAnimationVariableBool("IsFirstPerson") && !IsPlayerAimingOrScoped()
		PlayerRef.AttemptAnimationSetSwitch()
	endif
	if !inPowerArmorCached && !wasSuit && hasHeroSuitEquipped
		Debug.Notification("[Astro-Cosmos] Traje de Vuelo activo: [Y] Volar | Compatible con Carabina y Canon Orbital Astro-Cosmos")
	elseif inPowerArmorCached && !wasPATorso && hasCosmosPATorsoEquipped
		Debug.Notification("[Astro-Cosmos] Torso Propulsor PA activo: [Y] Volar | Compatible con Carabina y Canon Orbital Astro-Cosmos")
	endif
EndEvent

Event Actor.OnItemUnequipped(Actor akSender, Form akBaseObject, ObjectReference akReference)
	bool couldFly = CanPlayerFlyNow()
	RefreshPowerArmorCache()
	RefreshHeroSuitCache()
	RefreshCosmosPACache()
	RefreshHeroWeaponCache()
	RefreshPAWeaponCache()
	forceAuxCheck = true
	if !PlayerRef || !PlayerRef.Is3DLoaded() || IsPipboyOrMenuBusy()
		pendingPostPipboySync = true
		if !PlayerRef || !PlayerRef.Is3DLoaded()
			StartTimer(0.50, TIMER_POST_PIPBOY)
		endif
		return
	endif
	if couldFly && !CanPlayerFlyNow() && (isFloating || isAscending)
		Debug.Notification("[Astro-Cosmos] Propulsor desequipado en el aire: descendiendo...")
		StartControlledDescent(false)
	endif
	EnsureFlightAbilities()
EndEvent

Event Actor.OnSit(Actor akSender, ObjectReference akFurniture)
	StopFloating(false)
	StartTimer(0.5, TIMER_INIT)
EndEvent

Event Actor.OnGetUp(Actor akSender, ObjectReference akFurniture)
	StopFloating(false)
	StartTimer(0.5, TIMER_INIT)
EndEvent

Event Actor.OnRaceSwitchComplete(Actor akSender)
	StopFloating(false)
	RefreshPowerArmorCache()
	RefreshHeroSuitCache()
	RefreshCosmosPACache()
	RefreshHeroWeaponCache()
	RefreshPAWeaponCache()
	EnsureFlightAbilities()
	if inPowerArmorCached && hasCosmosPATorsoEquipped
		Debug.Notification("[Astro-Cosmos] Servoarmadura Astro-Cosmos lista: [Y] Volar | Compatible con Carabina y Canon Orbital Astro-Cosmos")
	endif
EndEvent

Event OnMenuOpenCloseEvent(string asMenuName, bool abOpening)
	if asMenuName == "ScopeMenu"
		scopeMenuOpen = abOpening
		if !abOpening
			aimHeld = false
			lastAimReleaseTime = Utility.GetCurrentRealTime()
		endif
		return
	endif
	if asMenuName == "PipboyMenu"
		pipboyMenuOpen = abOpening
		if abOpening
			CancelTimer(TIMER_POST_PIPBOY)
			; Mantener el vuelo estacionario intacto sin llamar jamas a StopFloating, ChangeAnimFlavor
			; ni AttemptAnimationSetSwitch mientras el Pip-Boy de Servoarmadura (Quick-Boy) se abre;
			; si estaba en pleno ascenso con [Y], asegurar la losa de levitacion bajo las botas.
			if isAscending
				jumpHeld = false
				isAscending = false
				if PlayerRef
					float curZ = PlayerRef.GetPositionZ()
					if isFloating || (curZ - takeoffZ) >= 12.0
						isFloating = true
						float px = PlayerRef.GetPositionX()
						float py = PlayerRef.GetPositionY()
						lockedZ = curZ - 1.5
						PlaceDualSupport(px, py, px, py, lockedZ)
					endif
				endif
			endif
		else
			lastPipboyCloseTime = Utility.GetCurrentRealTime()
			StartTimer(0.55, TIMER_POST_PIPBOY)
		endif
		return
	endif
	if abOpening && (isFloating || isAscending || isDescending || platEnabled || footstepsMuted)
		StopFloating(false)
	endif
EndEvent

bool Function IsPipboyOrMenuBusy()
	if pipboyMenuOpen
		return true
	endif
	if Utility.IsInMenuMode()
		return true
	endif
	if lastPipboyCloseTime > 0.0 && (Utility.GetCurrentRealTime() - lastPipboyCloseTime) < 0.50
		return true
	endif
	return false
EndFunction

Function RefreshPowerArmorCache()
	if !PlayerRef
		PlayerRef = Game.GetPlayer()
	endif
	if !PlayerRef
		inPowerArmorCached = false
		return
	endif
	if !powerArmorPerkCached
		powerArmorPerkCached = Game.GetFormFromFile(0x0001F8A9, "Fallout4.esm") as Perk
	endif
	if powerArmorPerkCached
		inPowerArmorCached = PlayerRef.HasPerk(powerArmorPerkCached)
	else
		inPowerArmorCached = PlayerRef.IsInPowerArmor()
	endif
EndFunction

Function RefreshHeroSuitCache()
	if !PlayerRef
		PlayerRef = Game.GetPlayer()
	endif
	if !PlayerRef
		hasHeroSuitEquipped = false
		return
	endif
	if !HeroFlightSuit
		HeroFlightSuit = Game.GetFormFromFile(0x00000800, "AeroArmorMod.esp") as Armor
	endif
	if HeroFlightSuit
		hasHeroSuitEquipped = PlayerRef.IsEquipped(HeroFlightSuit)
	else
		hasHeroSuitEquipped = false
	endif
EndFunction

Function RefreshCosmosPACache()
	if !PlayerRef
		PlayerRef = Game.GetPlayer()
	endif
	if !PlayerRef
		hasCosmosPATorsoEquipped = false
		return
	endif
	if !CosmosPATorsoKw
		CosmosPATorsoKw = Game.GetFormFromFile(0x0000081F, "AeroArmorMod.esp") as Keyword
	endif
	if !CosmosPATorso
		CosmosPATorso = Game.GetFormFromFile(0x00000820, "AeroArmorMod.esp") as Armor
	endif
	bool hasKw = (CosmosPATorsoKw && PlayerRef.WornHasKeyword(CosmosPATorsoKw))
	bool hasPiece = (CosmosPATorso && PlayerRef.IsEquipped(CosmosPATorso))
	hasCosmosPATorsoEquipped = (hasKw || hasPiece)
EndFunction

Function RefreshHeroWeaponCache()
	if !PlayerRef
		PlayerRef = Game.GetPlayer()
	endif
	if !PlayerRef
		hasHeroWeapEquipped = false
		return
	endif
	if !CosmosHeroWeapKw
		CosmosHeroWeapKw = Game.GetFormFromFile(0x00000847, "AeroArmorMod.esp") as Keyword
	endif
	if !CosmosHeroCarbine
		CosmosHeroCarbine = Game.GetFormFromFile(0x00000840, "AeroArmorMod.esp") as Weapon
	endif
	bool hasKw = (CosmosHeroWeapKw && PlayerRef.WornHasKeyword(CosmosHeroWeapKw))
	bool hasWeap = (CosmosHeroCarbine && PlayerRef.IsEquipped(CosmosHeroCarbine))
	hasHeroWeapEquipped = (hasKw || hasWeap)
EndFunction

Function RefreshPAWeaponCache()
	if !PlayerRef
		PlayerRef = Game.GetPlayer()
	endif
	if !PlayerRef
		hasPAWeapEquipped = false
		return
	endif
	if !CosmosPAWeapKw
		CosmosPAWeapKw = Game.GetFormFromFile(0x00000857, "AeroArmorMod.esp") as Keyword
	endif
	if !CosmosPACannon
		CosmosPACannon = Game.GetFormFromFile(0x00000850, "AeroArmorMod.esp") as Weapon
	endif
	bool hasKw = (CosmosPAWeapKw && PlayerRef.WornHasKeyword(CosmosPAWeapKw))
	bool hasWeap = (CosmosPACannon && PlayerRef.IsEquipped(CosmosPACannon))
	hasPAWeapEquipped = (hasKw || hasWeap)
EndFunction

bool Function IsAllowedFlightWeaponEquipped()
	if inPowerArmorCached
		if !hasCosmosPATorsoEquipped
			return false
		endif
	elseif !hasHeroSuitEquipped
		return false
	endif
	return hasHeroWeapEquipped || hasPAWeapEquipped
EndFunction

bool Function CanPlayerFlyNow()
	if inPowerArmorCached
		return hasCosmosPATorsoEquipped
	endif
	return hasHeroSuitEquipped
EndFunction

Function SetupFlightSystem(bool showNotice)
	PlayerRef = Game.GetPlayer()
	if !PlayerRef
		StartTimer(1.0, TIMER_INIT)
		return
	endif

	RegisterForRemoteEvent(PlayerRef, "OnPlayerLoadGame")
	if !PlayerRef.Is3DLoaded() || Utility.IsInMenuMode() || !Game.IsMovementControlsEnabled()
		StartTimer(1.0, TIMER_INIT)
		return
	endif

	lastLoadBootstrapRealTime = Utility.GetCurrentRealTime()
	isPrewarming = false
	isTimerTicking = false
	povTogglePending = false
	aimHeld = false
	scopeMenuOpen = false
	pipboyMenuOpen = false
	pendingPostPipboySync = false
	lastPipboyCloseTime = 0.0
	readyWeaponHeld = false
	readyWeaponDownTime = 0.0
	lastHolsterStartTime = 0.0
	DestroyPlatforms()
	SetFlightFootstepsMuted(false)
	if isFloating || isAscending || isDescending || has3rdPersonFlavor || pendingGroundFlavorReset
		StopFloating(false)
	else
		CancelTimer(TIMER_FLOAT)
		syncStep = 0
	endif

	RegisterForRemoteEvent(PlayerRef, "OnItemEquipped")
	RegisterForRemoteEvent(PlayerRef, "OnItemUnequipped")
	RegisterForRemoteEvent(PlayerRef, "OnSit")
	RegisterForRemoteEvent(PlayerRef, "OnGetUp")
	RegisterForRemoteEvent(PlayerRef, "OnRaceSwitchComplete")
	RegisterForMenuOpenCloseEvent("PipboyMenu")
	RegisterForMenuOpenCloseEvent("LoadingMenu")
	RegisterForMenuOpenCloseEvent("ScopeMenu")

	RegisterForControl("Jump")
	RegisterForControl("Sneak")
	RegisterForControl("Melee")
	RegisterForControl("Sprint")
	RegisterForControl("TogglePOV")
	RegisterForControl("ZoomIn")
	RegisterForControl("ReadyWeapon")
	RegisterForControl("PrimaryAttack")
	RegisterForControl("SecondaryAttack")
	RegisterForKey(KEY_H)

	if !HeroFlightSuit
		HeroFlightSuit = Game.GetFormFromFile(0x00000800, "AeroArmorMod.esp") as Armor
	endif
	if !CosmosHeroCarbine
		CosmosHeroCarbine = Game.GetFormFromFile(0x00000840, "AeroArmorMod.esp") as Weapon
	endif
	if !CosmosPACannon
		CosmosPACannon = Game.GetFormFromFile(0x00000850, "AeroArmorMod.esp") as Weapon
	endif
	starterSuitGranted = true
	starterPAGranted = true
	starterHeroWeapGranted = true
	starterPAWeapGranted = true

	RefreshPowerArmorCache()
	RefreshHeroSuitCache()
	RefreshCosmosPACache()
	RefreshHeroWeaponCache()
	RefreshPAWeaponCache()
	EnsureFlightAbilities()
	CleanupOrphanPlatforms()
	EnsurePlatformPool()
	HidePlatforms()

	if showNotice
		if inPowerArmorCached && hasCosmosPATorsoEquipped
			Debug.Notification("[Astro-Cosmos] Servoarmadura Astro-Cosmos activa: [Y] Subir/Volar | [L3] Turbo | [RS/RB] Bajar")
		elseif !inPowerArmorCached && hasHeroSuitEquipped
			Debug.Notification("[Astro-Cosmos] Traje equipado: [Y] Subir/Volar | [L3] Turbo | [RS/RB] Bajar")
		endif
	endif
EndFunction

Function SetFlightFootstepsMuted(bool abMute)
	if !PlayerFootstepCat
		PlayerFootstepCat = Game.GetFormFromFile(0x000F5FFC, "Fallout4.esm") as SoundCategory
	endif
	if !PlayerFootstepSubCat
		PlayerFootstepSubCat = Game.GetFormFromFile(0x00214018, "Fallout4.esm") as SoundCategory
	endif

	if abMute
		if !footstepsMuted
			if PlayerFootstepCat
				PlayerFootstepCat.Mute()
			endif
			if PlayerFootstepSubCat
				PlayerFootstepSubCat.Mute()
			endif
			footstepsMuted = true
		endif
	else
		if PlayerFootstepCat
			PlayerFootstepCat.UnMute()
		endif
		if PlayerFootstepSubCat
			PlayerFootstepSubCat.UnMute()
		endif
		footstepsMuted = false
	endif
EndFunction

Function EnsureFlightAbilities()
	if !PlayerRef
		PlayerRef = Game.GetPlayer()
	endif
	if !PlayerRef
		return
	endif

	RefreshPowerArmorCache()
	RefreshHeroSuitCache()
	RefreshCosmosPACache()

	if !CustomFlightSpell
		CustomFlightSpell = Game.GetFormFromFile(0x00000808, "AeroArmorMod.esp") as Spell
	endif
	if !CosmicRadShieldPerk
		CosmicRadShieldPerk = Game.GetFormFromFile(0x0000081B, "AeroArmorMod.esp") as Perk
	endif

	; El vuelo y el escudo antirradiacion cosmico estan activos UNICAMENTE si:
	;   1) Fuera de Servoarmadura: lleva puesto el Traje de Vuelo Astro-Cosmos (0x01000800), o
	;   2) Dentro de Servoarmadura: lleva puesto el Torso Propulsor Astro-Cosmos (0x01000820).
	if !CanPlayerFlyNow()
		if CustomFlightSpell && PlayerRef.HasSpell(CustomFlightSpell)
			PlayerRef.RemoveSpell(CustomFlightSpell)
		endif
		if CosmicRadShieldPerk && PlayerRef.HasPerk(CosmicRadShieldPerk)
			PlayerRef.RemovePerk(CosmicRadShieldPerk)
		endif
		if !isDescending && !isFloating && !isAscending
			if NoFallDamagePerk && PlayerRef.HasPerk(NoFallDamagePerk)
				PlayerRef.RemovePerk(NoFallDamagePerk)
			endif
			if NoImpactLandKeyword && PlayerRef.HasKeyword(NoImpactLandKeyword)
				PlayerRef.RemoveKeyword(NoImpactLandKeyword)
			endif
		endif
		return
	endif

	if CosmicRadShieldPerk && !PlayerRef.HasPerk(CosmicRadShieldPerk)
		PlayerRef.AddPerk(CosmicRadShieldPerk)
	endif

	if !NoFallDamagePerk
		NoFallDamagePerk = Game.GetFormFromFile(0x0002A6FC, "Fallout4.esm") as Perk
	endif
	if NoFallDamagePerk && !PlayerRef.HasPerk(NoFallDamagePerk)
		PlayerRef.AddPerk(NoFallDamagePerk)
	endif

	if !NoImpactLandKeyword
		NoImpactLandKeyword = Game.GetFormFromFile(0x001E2F29, "Fallout4.esm") as Keyword
	endif
	if NoImpactLandKeyword && !PlayerRef.HasKeyword(NoImpactLandKeyword)
		PlayerRef.AddKeyword(NoImpactLandKeyword)
	endif

	if !ActionPointsAV
		ActionPointsAV = Game.GetFormFromFile(0x000002D5, "Fallout4.esm") as ActorValue
	endif
	if ActionPointsAV
		PlayerRef.RestoreValue(ActionPointsAV, 9999.0)
	endif

	Spell oldVanillaSpell = Game.GetFormFromFile(0x0012772C, "Fallout4.esm") as Spell
	if oldVanillaSpell && PlayerRef.HasSpell(oldVanillaSpell)
		PlayerRef.RemoveSpell(oldVanillaSpell)
	endif

	if CustomFlightSpell && !PlayerRef.HasSpell(CustomFlightSpell)
		PlayerRef.AddSpell(CustomFlightSpell, false)
	endif
EndFunction

Function RecreatePlatforms()
	DestroyPlatforms()
	CleanupOrphanPlatforms()
	EnsurePlatformPool()
	HidePlatforms()
EndFunction

Function EnsurePlatformPool()
	; Mantiene en pool 2 plataformas invisibles ya habilitadas en Havok y aparcadas 3500u bajo tierra,
	; evitando por completo PlaceAtMe/Delete/EnableNoWait durante el segundo y sucesivos despegues.
	if !PlayerRef || isPrewarming
		return
	endif
	isPrewarming = true
	if !HoverPlatformForm
		HoverPlatformForm = Game.GetFormFromFile(0x00000809, "AeroArmorMod.esp")
		if !HoverPlatformForm
			HoverPlatformForm = Game.GetFormFromFile(0x00067A4B, "Fallout4.esm")
		endif
	endif
	if !HoverPlatformForm
		isPrewarming = false
		return
	endif

	ObjectReference refA = platA
	if !refA || refA.IsDeleted()
		refA = PlayerRef.PlaceAtMe(HoverPlatformForm, 1, false, false, false)
		if refA
			refA.SetAngle(0.0, 0.0, 0.0)
		endif
		platA = refA
	endif

	ObjectReference refB = platB
	if !refB || refB.IsDeleted()
		refB = PlayerRef.PlaceAtMe(HoverPlatformForm, 1, false, false, false)
		if refB
			refB.SetAngle(0.0, 0.0, 0.0)
		endif
		platB = refB
	endif

	isPrewarming = false
EndFunction

Function PrewarmPlatforms(float tx, float ty, float tz, int expectedSession)
	if !PlayerRef || isPrewarming
		return
	endif
	if expectedSession != flightSessionId || isDescending || (!isFloating && !isAscending)
		return
	endif

	EnsurePlatformPool()
	ObjectReference refA = platA
	ObjectReference refB = platB
	if !refA || !refB
		return
	endif
	if expectedSession != flightSessionId || isDescending || (!isFloating && !isAscending)
		HidePlatforms()
		return
	endif

	Cell pCell = PlayerRef.GetParentCell()
	if refA.GetParentCell() != pCell
		refA.MoveTo(PlayerRef, tx - PlayerRef.GetPositionX(), ty - PlayerRef.GetPositionY(), tz - PlayerRef.GetPositionZ(), false)
		refA.SetAngle(0.0, 0.0, 0.0)
	else
		refA.SetPosition(tx, ty, tz)
	endif

	if refB.GetParentCell() != pCell
		refB.MoveTo(PlayerRef, tx - PlayerRef.GetPositionX(), ty - PlayerRef.GetPositionY(), tz - PlayerRef.GetPositionZ(), false)
		refB.SetAngle(0.0, 0.0, 0.0)
	else
		refB.SetPosition(tx, ty, tz)
	endif

	if expectedSession != flightSessionId || isDescending || (!isFloating && !isAscending)
		HidePlatforms()
		return
	endif

	activePlat = 0
	cellCheckCounter = 0
	lastPlatX = tx
	lastPlatY = ty
	lastRelayPlayerX = tx
	lastRelayPlayerY = ty
	platEnabled = true
EndFunction

Function PlaceDualSupport(float leadX, float leadY, float px, float py, float tz)
	; Coloca simultaneamente refA bajo los pies (px, py, tz) y refB por delante (leadX, leadY, tz)
	; en solo 2 llamadas SetPosition (~30 ms), garantizando 512u continuas de suelo solido al bloquear
	; el vuelo tras subir con [Y] o al compensar caidas verticales.
	int entrySession = flightSessionId
	if !PlayerRef || isDescending || (!isFloating && !isAscending)
		return
	endif
	ObjectReference refA = platA
	ObjectReference refB = platB
	if !refA || !refB || refA.IsDeleted() || refB.IsDeleted()
		EnsurePlatformPool()
		refA = platA
		refB = platB
		if !refA || !refB || entrySession != flightSessionId || isDescending || (!isFloating && !isAscending)
			return
		endif
	endif

	Cell pCell = PlayerRef.GetParentCell()
	if isDescending || (!isFloating && !isAscending) || entrySession != flightSessionId
		return
	endif
	if refA.GetParentCell() != pCell
		refA.MoveTo(PlayerRef, 0.0, 0.0, tz - PlayerRef.GetPositionZ(), false)
		refA.SetAngle(0.0, 0.0, 0.0)
	endif
	if isDescending || (!isFloating && !isAscending)
		HidePlatforms()
		return
	elseif entrySession != flightSessionId
		return
	endif
	refA.SetPosition(px, py, tz)
	if isDescending || (!isFloating && !isAscending)
		HidePlatforms()
		return
	elseif entrySession != flightSessionId
		return
	endif

	if refB.GetParentCell() != pCell
		refB.MoveTo(PlayerRef, leadX - px, leadY - py, tz - PlayerRef.GetPositionZ(), false)
		refB.SetAngle(0.0, 0.0, 0.0)
	endif
	if isDescending || (!isFloating && !isAscending)
		HidePlatforms()
		return
	elseif entrySession != flightSessionId
		return
	endif
	refB.SetPosition(leadX, leadY, tz)
	if isDescending || (!isFloating && !isAscending)
		HidePlatforms()
		return
	elseif entrySession != flightSessionId
		return
	endif

	activePlat = 1
	lastPlatX = leadX
	lastPlatY = leadY
	lastRelayPlayerX = px
	lastRelayPlayerY = py
	platEnabled = true
EndFunction

Function CleanupOrphanPlatforms()
	if !PlayerRef
		PlayerRef = Game.GetPlayer()
	endif
	if !PlayerRef
		return
	endif
	if !HoverPlatformForm
		HoverPlatformForm = Game.GetFormFromFile(0x00000809, "AeroArmorMod.esp")
		if !HoverPlatformForm
			HoverPlatformForm = Game.GetFormFromFile(0x00067A4B, "Fallout4.esm")
		endif
	endif
	if !HoverPlatformForm
		return
	endif
	float px = PlayerRef.GetPositionX()
	float py = PlayerRef.GetPositionY()
	float pz = PlayerRef.GetPositionZ()
	ObjectReference[] found = PlayerRef.FindAllReferencesOfType(HoverPlatformForm, 10000.0)
	int i = 0
	while i < found.Length
		ObjectReference ref = found[i]
		if ref && ref != platA && ref != platB
			ref.SetPosition(px, py, pz - 3500.0)
			ref.DisableNoWait()
			ref.Delete()
		endif
		i += 1
	endWhile
EndFunction

Function AdvancePlatformRelay(float tx, float ty, float tz, float playerX, float playerY)
	; Relevo alterno ultrarrapido (1 sola llamada latente SetPosition en el 92% de los ticks):
	; Mueve UNICAMENTE la plataforma inactiva mientras la activa sostiene al jugador, soportando
	; velocidades > 550 u/s (esprintar con L3 en 3a y 1a persona) sin perder jamas el suelo.
	int entrySession = flightSessionId
	if !PlayerRef || isPrewarming || isDescending || (!isFloating && !isAscending)
		return
	endif

	ObjectReference refA = platA
	ObjectReference refB = platB
	if !platEnabled || !refA || !refB || refA.IsDeleted() || refB.IsDeleted()
		PlaceDualSupport(tx, ty, playerX, playerY, tz)
		return
	endif

	cellCheckCounter += 1
	bool checkCell = (cellCheckCounter >= 12)
	if checkCell
		cellCheckCounter = 0
	endif

	ObjectReference targetRef = refB
	int nextActivePlat = 1
	if activePlat != 0
		targetRef = refA
		nextActivePlat = 0
	endif

	if checkCell && targetRef.GetParentCell() != PlayerRef.GetParentCell()
		if isDescending || (!isFloating && !isAscending) || entrySession != flightSessionId
			return
		endif
		targetRef.MoveTo(PlayerRef, 0.0, 0.0, tz - PlayerRef.GetPositionZ(), false)
		targetRef.SetAngle(0.0, 0.0, 0.0)
	endif
	if isDescending || (!isFloating && !isAscending) || entrySession != flightSessionId
		return
	endif

	targetRef.SetPosition(tx, ty, tz)
	if isDescending || (!isFloating && !isAscending)
		HidePlatforms()
		return
	elseif entrySession != flightSessionId
		return
	endif

	activePlat = nextActivePlat
	lastPlatX = tx
	lastPlatY = ty
	lastRelayPlayerX = playerX
	lastRelayPlayerY = playerY
EndFunction

Function SyncInactivePlatform(float tx, float ty, float tz)
	if !PlayerRef || !platEnabled || isPrewarming || isDescending || (!isFloating && !isAscending)
		return
	endif
	ObjectReference refA = platA
	ObjectReference refB = platB
	if activePlat == 0
		if refB
			refB.SetPosition(tx, ty, tz)
		endif
	else
		if refA
			refA.SetPosition(tx, ty, tz)
		endif
	endif
	lastRelayPlayerX = tx
	lastRelayPlayerY = ty
EndFunction

Function HidePlatforms()
	; Aparca las dos plataformas del pool 3500u bajo tierra en 1 fotograma sin destruirlas,
	; dejandolas listas e instantaneas para el siguiente despegue.
	int hideSession = flightSessionId
	if isFloating || isAscending
		return
	endif
	platEnabled = false
	aimBackOffsetActive = false
	ObjectReference refA = platA
	ObjectReference refB = platB
	if !refA && !refB
		return
	endif
	if !PlayerRef
		PlayerRef = Game.GetPlayer()
	endif
	if !PlayerRef
		return
	endif
	float px = PlayerRef.GetPositionX()
	float py = PlayerRef.GetPositionY()
	float pz = PlayerRef.GetPositionZ()
	if hideSession != flightSessionId || isFloating || isAscending
		return
	endif
	if refA && !refA.IsDeleted()
		refA.SetPosition(px, py, pz - 3500.0)
	endif
	if hideSession != flightSessionId || isFloating || isAscending
		return
	endif
	if refB && !refB.IsDeleted()
		refB.SetPosition(px, py, pz - 3500.0)
	endif
EndFunction

Function DestroyPlatforms()
	platEnabled = false
	ObjectReference refA = platA
	ObjectReference refB = platB
	platA = None
	platB = None
	if refA && !refA.IsDeleted()
		refA.DisableNoWait()
		refA.Delete()
	endif
	if refB && !refB.IsDeleted()
		refB.DisableNoWait()
		refB.Delete()
	endif
EndFunction

Function ClearCustomSubgraphKeywords()
	Keyword fArch = Game.GetFormFromFile(0x00000812, "AeroArmorMod.esp") as Keyword
	Keyword dArch = Game.GetFormFromFile(0x00000813, "AeroArmorMod.esp") as Keyword
	Keyword fFlav = Game.GetFormFromFile(0x00000816, "AeroArmorMod.esp") as Keyword
	Keyword dFlav = Game.GetFormFromFile(0x00000817, "AeroArmorMod.esp") as Keyword
	if fArch
		PlayerRef.RemoveKeyword(fArch)
	endif
	if dArch
		PlayerRef.RemoveKeyword(dArch)
	endif
	if fFlav
		PlayerRef.RemoveKeyword(fFlav)
	endif
	if dFlav
		PlayerRef.RemoveKeyword(dFlav)
	endif
EndFunction

Function ExecuteGroundSubgraphReset()
	if !PlayerRef
		PlayerRef = Game.GetPlayer()
	endif
	if !PlayerRef
		return
	endif
	if !PlayerRef.Is3DLoaded() || IsPipboyOrMenuBusy()
		pendingGroundFlavorReset = true
		landCleanTicks = 0
		landSwitchFollowups = 4
		syncStep = 0
		StartTimer(0.25, TIMER_LAND_CLEAN)
		return
	endif
	RefreshPowerArmorCache()
	bool is1stP = PlayerRef.GetAnimationVariableBool("IsFirstPerson")
	Keyword fArch = Game.GetFormFromFile(0x00000812, "AeroArmorMod.esp") as Keyword
	Keyword dArch = Game.GetFormFromFile(0x00000813, "AeroArmorMod.esp") as Keyword
	Keyword fFlav = Game.GetFormFromFile(0x00000816, "AeroArmorMod.esp") as Keyword
	Keyword dFlav = Game.GetFormFromFile(0x00000817, "AeroArmorMod.esp") as Keyword
	Keyword bombBabyFlav = Game.GetFormFromFile(0x00178A65, "Fallout4.esm") as Keyword
	Keyword bombReactFlav = Game.GetFormFromFile(0x00160496, "Fallout4.esm") as Keyword
	Keyword militaryFlav = Game.GetFormFromFile(0x0015F755, "Fallout4.esm") as Keyword

	if fArch
		PlayerRef.RemoveKeyword(fArch)
	endif
	if dArch
		PlayerRef.RemoveKeyword(dArch)
	endif
	if fFlav
		PlayerRef.RemoveKeyword(fFlav)
	endif
	if bombBabyFlav
		PlayerRef.RemoveKeyword(bombBabyFlav)
	endif
	if bombReactFlav
		PlayerRef.RemoveKeyword(bombReactFlav)
	endif
	if militaryFlav
		PlayerRef.RemoveKeyword(militaryFlav)
	endif

	bool okG = false
	if inPowerArmorCached && !is1stP && dFlav
		; En Servoarmadura 3a persona, conmutamos al instante fuera de Military (6102835159731828685.txt)
		; hacia dFlav (AeroArmor_DescentFlavorKw -> 14810735168864942029.txt, subgrafo nativo de tierra),
		; cuyo clip To_* no existe (igual que To_Military en el despegue), forzando el cambio inmediato
		; en BSAnimationGraphManager sin esperar a To_Normal.hkx. Luego TIMER_LAND_CLEAN limpia a None.
		PlayerRef.RemoveKeyword(dFlav)
		okG = PlayerRef.ChangeAnimFlavor(dFlav)
	else
		if dFlav
			PlayerRef.RemoveKeyword(dFlav)
		endif
		okG = PlayerRef.ChangeAnimFlavor(None)
	endif
	PlayerRef.AttemptAnimationSetSwitch()

	if is1stP && has3rdPersonFlavor
		pending3rdPersonCleanup = true
	else
		pending3rdPersonCleanup = false
	endif
	has3rdPersonFlavor = false
	pendingGroundFlavorReset = false
	povTogglePending = false
	active3rdPersonFlavorMode = 0
	syncStep = 0
	Debug.Trace("[Aero-Mod] AnimState -> 0 (Ground) flavReset=" + okG + " is1stP=" + is1stP + " PA=" + inPowerArmorCached)
EndFunction

bool Function IsPlayerAimingOrScoped()
	if !PlayerRef
		return false
	endif
	if !PlayerRef.IsWeaponDrawn()
		aimHeld = false
		scopeMenuOpen = false
		return false
	endif
	if scopeMenuOpen
		return true
	endif
	if aimHeld
		return true
	endif
	if lastAimReleaseTime > 0.0 && (Utility.GetCurrentRealTime() - lastAimReleaseTime) < 0.45
		return true
	endif
	return false
EndFunction

bool Function IsWeaponHolsteringNow()
	; Al guardar (manteniendo ReadyWeapon) un arma no autorizada, la animacion de enfundado
	; tarda ~1.2-1.8 s con IsWeaponDrawn() todavia en true. Evitamos bloquear el siguiente despegue
	; ni lanzar descenso forzado durante esa ventana mientras ReadyWeapon se mantuvo >= 0.15 s.
	if !PlayerRef || !PlayerRef.IsWeaponDrawn()
		return false
	endif
	float now = Utility.GetCurrentRealTime()
	if readyWeaponHeld && readyWeaponDownTime > 0.0
		float holdDur = now - readyWeaponDownTime
		if holdDur >= 0.15 && holdDur < 2.20
			return true
		endif
	endif
	if lastHolsterStartTime > 0.0 && (now - lastHolsterStartTime) < 1.80
		return true
	endif
	return false
EndFunction

Function ApplyFlightAnimState(int targetMode)
	if !PlayerRef
		PlayerRef = Game.GetPlayer()
	endif
	if !PlayerRef
		return
	endif
	if !PlayerRef.Is3DLoaded()
		if targetMode == 0 && (syncStep != 0 || has3rdPersonFlavor || pending3rdPersonCleanup || pendingGroundFlavorReset)
			pendingGroundFlavorReset = true
			landCleanTicks = 0
			landSwitchFollowups = 4
			syncStep = 0
			StartTimer(0.30, TIMER_LAND_CLEAN)
		elseif targetMode != 0
			pendingPostPipboySync = true
			StartTimer(0.30, TIMER_POST_PIPBOY)
		endif
		return
	endif

	bool is1stP = PlayerRef.GetAnimationVariableBool("IsFirstPerson")

	if targetMode == 0
		if IsPipboyOrMenuBusy()
			if syncStep != 0 || has3rdPersonFlavor || pending3rdPersonCleanup || pendingGroundFlavorReset
				pendingGroundFlavorReset = true
				landCleanTicks = 0
				landSwitchFollowups = 4
				syncStep = 0
				StartTimer(0.25, TIMER_LAND_CLEAN)
			endif
			return
		endif
		if syncStep == 0 && !has3rdPersonFlavor && !pending3rdPersonCleanup && !pendingGroundFlavorReset
			PlayerRef.AttemptAnimationSetSwitch()
			return
		endif
		if !is1stP && PlayerRef.GetAnimationVariableBool("bInJumpState")
			; Esperar unicamente si aun sigue en el aire (bInJumpState); en cuanto las botas tocan suelo
			; ejecutamos ExecuteGroundSubgraphReset() al instante sin esperar el segundo entero de bInLandingState.
			pendingGroundFlavorReset = true
			landCleanTicks = 0
			landSwitchFollowups = 4
			syncStep = 0
			StartTimer(0.06, TIMER_LAND_CLEAN)
			return
		endif
		ExecuteGroundSubgraphReset()
		landCleanTicks = 0
		landSwitchFollowups = 4
		StartTimer(0.20, TIMER_LAND_CLEAN)
		return
	endif

	if IsPipboyOrMenuBusy()
		pendingPostPipboySync = true
		return
	endif

	CancelTimer(TIMER_LAND_CLEAN)
	pendingGroundFlavorReset = false
	landSwitchFollowups = 0

	if is1stP
		; Si el jugador esta usando la mira telescopica 6x desde 3a persona, el motor activa temporalmente
		; IsFirstPerson = true y ScopeMenu. Nunca tocar ChangeAnimFlavor ni AttemptAnimationSetSwitch
		; mientras apunta, para no expulsarle de la mira telescopica.
		if IsPlayerAimingOrScoped()
			syncStep = targetMode
			return
		endif
		if has3rdPersonFlavor && povTogglePending
			ClearCustomSubgraphKeywords()
			Keyword militaryFlav1p = Game.GetFormFromFile(0x0015F755, "Fallout4.esm") as Keyword
			PlayerRef.ChangeAnimFlavor(None)
			if militaryFlav1p
				PlayerRef.RemoveKeyword(militaryFlav1p)
			endif
			PlayerRef.AttemptAnimationSetSwitch()
			pending3rdPersonCleanup = true
			has3rdPersonFlavor = false
			active3rdPersonFlavorMode = 0
		endif
		povTogglePending = false
		syncStep = targetMode
		return
	endif

	povTogglePending = false

	if inPowerArmorCached
		Keyword militaryFlavPA = Game.GetFormFromFile(0x0015F755, "Fallout4.esm") as Keyword
		if targetMode == 1
			if has3rdPersonFlavor && active3rdPersonFlavorMode == 1
				syncStep = 1
				return
			endif
			ClearCustomSubgraphKeywords()
			pending3rdPersonCleanup = false
			if militaryFlavPA
				PlayerRef.RemoveKeyword(militaryFlavPA)
				bool okPA = PlayerRef.ChangeAnimFlavor(militaryFlavPA)
				if !scopeMenuOpen
					PlayerRef.AttemptAnimationSetSwitch()
				endif
				has3rdPersonFlavor = true
				active3rdPersonFlavorMode = 1
				syncStep = 1
				Debug.Trace("[Aero-Mod] AnimState -> 1 (PA 3rdP Flight) flavOk=" + okPA)
			endif
		else
			; En descenso (targetMode == 2), mantenemos el subgrafo de vuelo en el aire para que si el
			; jugador frena el descenso antes de tocar tierra conserve una postura fluida sin doblar
			; rodillas en el cielo; en cuanto toca suelo firme, ExecuteGroundSubgraphReset() conmuta al
			; instante al subgrafo nativo de tierra (14810735168864942029.txt).
			syncStep = 2
		endif
		return
	endif

	if has3rdPersonFlavor && active3rdPersonFlavorMode == targetMode
		syncStep = targetMode
		return
	endif

	ClearCustomSubgraphKeywords()
	pending3rdPersonCleanup = false

	if targetMode == 1
		Keyword bombBabyFlav = Game.GetFormFromFile(0x00178A65, "Fallout4.esm") as Keyword
		if bombBabyFlav
			PlayerRef.RemoveKeyword(bombBabyFlav)
			bool okH = PlayerRef.ChangeAnimFlavor(bombBabyFlav)
			if PlayerRef.IsWeaponDrawn() && !scopeMenuOpen
				PlayerRef.AttemptAnimationSetSwitch()
			endif
			has3rdPersonFlavor = true
			active3rdPersonFlavorMode = 1
			syncStep = 1
			Debug.Trace("[Aero-Mod] AnimState -> 1 (3rdP Flight) flavOk=" + okH)
		endif
	elseif targetMode == 2
		Keyword bombReactFlav = Game.GetFormFromFile(0x00160496, "Fallout4.esm") as Keyword
		if bombReactFlav
			PlayerRef.RemoveKeyword(bombReactFlav)
			bool okHD = PlayerRef.ChangeAnimFlavor(bombReactFlav)
			if PlayerRef.IsWeaponDrawn() && !scopeMenuOpen
				PlayerRef.AttemptAnimationSetSwitch()
			endif
			has3rdPersonFlavor = true
			active3rdPersonFlavorMode = 2
			syncStep = 2
			Debug.Trace("[Aero-Mod] AnimState -> 2 (3rdP Descent) flavOk=" + okHD)
		endif
	endif
EndFunction

Function StartControlledDescent(bool showWeaponNotice)
	flightSessionId += 1
	jumpHeld = false
	isFloating = false
	isAscending = false
	isDescending = true
	hasFallenDuringDescent = false
	sprintBoostActive = false
	justStartedDescent = true
	justStoppedDescent = false
	brakePulse = false
	climbTicks = 0
	landedTicks = 0
	SetFlightFootstepsMuted(true)
	HidePlatforms()
	ApplyFlightAnimState(2)
	if PlayerRef && PlayerRef.IsSneaking()
		PlayerRef.StartSneaking()
	endif
	if showWeaponNotice
		Debug.Notification("[Astro-Cosmos] En vuelo solo son compatibles la Carabina y el Canon Orbital Astro-Cosmos: descendiendo...")
	endif
	if !isTimerTicking
		StartTimer(0.03, TIMER_FLOAT)
	endif
EndFunction

Function StopFloating(bool showNotice)
	flightSessionId += 1
	int stopSession = flightSessionId
	isFloating = false
	isAscending = false
	isDescending = false
	hasFallenDuringDescent = false
	sprintBoostActive = false
	forceAuxCheck = false
	povTogglePending = false
	aimHeld = false
	scopeMenuOpen = false
	lastAimReleaseTime = 0.0
	readyWeaponHeld = false
	justStartedDescent = false
	justStoppedDescent = false
	jumpHeld = false
	brakePulse = false
	climbTicks = 0
	landedTicks = 0
	auxCheckCounter = 0
	CancelTimer(TIMER_FLOAT)
	HidePlatforms()
	SetFlightFootstepsMuted(false)
	if ActionPointsAV && PlayerRef
		PlayerRef.RestoreValue(ActionPointsAV, 9999.0)
	endif
	if stopSession != flightSessionId || isFloating || isAscending || isDescending
		return
	endif
	syncStep = -1
	ApplyFlightAnimState(0)
	if PlayerRef && PlayerRef.IsSneaking()
		PlayerRef.StartSneaking()
	endif
	if showNotice
		Debug.Notification("[Astro-Cosmos] Aterrizaje completado.")
	endif
	if !CanPlayerFlyNow()
		EnsureFlightAbilities()
	endif
EndFunction

Event OnControlDown(string control)
	if Utility.IsInMenuMode()
		return
	endif
	if !PlayerRef
		PlayerRef = Game.GetPlayer()
	endif
	if !PlayerRef
		return
	endif

	if control == "Jump"
		if !CanPlayerFlyNow()
			RefreshPowerArmorCache()
			RefreshHeroSuitCache()
			RefreshCosmosPACache()
			if !CanPlayerFlyNow()
				return
			endif
			EnsureFlightAbilities()
		endif
		if PlayerRef.IsWeaponDrawn() && !IsWeaponHolsteringNow()
			RefreshHeroWeaponCache()
			RefreshPAWeaponCache()
			if !IsAllowedFlightWeaponEquipped()
				return
			endif
		endif

		bool wasAirborne = (isFloating || isDescending)
		bool wasDescendingBeforeJump = isDescending
		flightSessionId += 1
		int mySession = flightSessionId
		takeoffRealTime = Utility.GetCurrentRealTime()
		jumpHeld = true
		isAscending = true
		isDescending = false
		hasFallenDuringDescent = false
		justStartedDescent = false
		justStoppedDescent = false
		brakePulse = false
		landedTicks = 0
		pendingGroundFlavorReset = false
		landSwitchFollowups = 0
		CancelTimer(TIMER_LAND_CLEAN)

		if !ActionPointsAV
			ActionPointsAV = Game.GetFormFromFile(0x000002D5, "Fallout4.esm") as ActorValue
		endif
		if ActionPointsAV
			PlayerRef.RestoreValue(ActionPointsAV, 9999.0)
		endif
		if !jumpHeld || mySession != flightSessionId || !isAscending || isDescending
			isAscending = false
			return
		endif

		float px = PlayerRef.GetPositionX()
		float py = PlayerRef.GetPositionY()
		float curZ = PlayerRef.GetPositionZ()
		if !jumpHeld || mySession != flightSessionId || !isAscending || isDescending
			isAscending = false
			return
		endif

		lastPlayerX = px
		lastPlayerY = py
		lastRelayPlayerX = px
		lastRelayPlayerY = py
		lastZ = curZ

		if !wasAirborne
			; Despegue desde tierra sin bloquear el lock del Quest en PlaceAtMe/PrewarmPlatforms:
			; las plataformas ya estan en pool bajo tierra y TIMER_FLOAT arranca en el acto (25 ms).
			climbTicks = 0
			takeoffZ = curZ
			lockedZ = curZ
		else
			isFloating = true
			climbTicks = 4
			if wasDescendingBeforeJump
				lockedZ = curZ - 4.0
			else
				lockedZ = curZ - 12.0
			endif
			forceAuxCheck = true
			SetFlightFootstepsMuted(true)
			PlaceDualSupport(px, py, px, py, lockedZ)
			if !jumpHeld || mySession != flightSessionId || !isAscending || isDescending
				isAscending = false
				return
			endif
			curZ = PlayerRef.GetPositionZ()
			lockedZ = curZ - 2.0
			lastZ = curZ
			ApplyFlightAnimState(1)
			if !jumpHeld || mySession != flightSessionId || !isAscending || isDescending
				isAscending = false
				return
			endif
		endif

		if !isTimerTicking
			StartTimer(0.025, TIMER_FLOAT)
		endif

	elseif control == "Sprint"
		if isFloating || isAscending
			sprintBoostActive = true
		endif

	elseif control == "TogglePOV" || control == "ZoomIn"
		if !scopeMenuOpen && !aimHeld
			povTogglePending = true
			if isFloating || isAscending || isDescending
				forceAuxCheck = true
			endif
		endif

	elseif control == "SecondaryAttack"
		if PlayerRef.IsWeaponDrawn()
			aimHeld = true
		endif

	elseif control == "ReadyWeapon"
		if PlayerRef.IsWeaponDrawn()
			readyWeaponHeld = true
			readyWeaponDownTime = Utility.GetCurrentRealTime()
			if !ActionPointsAV
				ActionPointsAV = Game.GetFormFromFile(0x000002D5, "Fallout4.esm") as ActorValue
			endif
			if ActionPointsAV
				PlayerRef.RestoreValue(ActionPointsAV, 9999.0)
			endif
		else
			readyWeaponHeld = false
			readyWeaponDownTime = 0.0
		endif
		if isFloating || isAscending || isDescending
			forceAuxCheck = true
		endif

	elseif control == "PrimaryAttack"
		if isFloating || isAscending || isDescending
			forceAuxCheck = true
		endif

	elseif control == "Sneak" || (control == "Melee" && !PlayerRef.IsWeaponDrawn())
		if isFloating || isAscending || isDescending
			if !isDescending
				StartControlledDescent(false)
			else
				if platEnabled
					HidePlatforms()
				endif
				forceAuxCheck = true
			endif
		endif
	endif
EndEvent

Event OnControlUp(string control, float time)
	if control == "SecondaryAttack"
		aimHeld = false
		lastAimReleaseTime = Utility.GetCurrentRealTime()
		return
	elseif control == "ReadyWeapon"
		bool wasHolsterHold = readyWeaponHeld
		readyWeaponHeld = false
		readyWeaponDownTime = 0.0
		if wasHolsterHold && time >= 0.15 && !Utility.IsInMenuMode()
			lastHolsterStartTime = Utility.GetCurrentRealTime()
			if !ActionPointsAV
				ActionPointsAV = Game.GetFormFromFile(0x000002D5, "Fallout4.esm") as ActorValue
			endif
			if ActionPointsAV && PlayerRef
				PlayerRef.RestoreValue(ActionPointsAV, 9999.0)
			endif
		endif
		if isFloating || isAscending || isDescending
			forceAuxCheck = true
		endif
		return
	endif
	if Utility.IsInMenuMode()
		if control == "Jump"
			jumpHeld = false
		endif
		return
	endif
	if !PlayerRef
		PlayerRef = Game.GetPlayer()
	endif
	if !PlayerRef
		return
	endif

	if control == "Jump"
		if !CanPlayerFlyNow() && !isFloating && !isAscending && !isDescending
			return
		endif
		if !isFloating && !isAscending && PlayerRef.IsWeaponDrawn() && !IsWeaponHolsteringNow()
			RefreshHeroWeaponCache()
			RefreshPAWeaponCache()
			if !IsAllowedFlightWeaponEquipped()
				if time >= 0.35
					Debug.Notification("[Astro-Cosmos] En vuelo solo puedes usar la Carabina o el Canon Orbital Astro-Cosmos.")
				endif
				return
			endif
		endif

		if isDescending || (!jumpHeld && !isAscending)
			return
		endif
		flightSessionId += 1
		int mySession = flightSessionId
		jumpHeld = false
		isAscending = false

		float curZ = PlayerRef.GetPositionZ()
		if mySession != flightSessionId || jumpHeld || isAscending || isDescending
			return
		endif
		if !isFloating && time < 0.18 && (curZ - takeoffZ) < 12.0
			StopFloating(false)
			return
		endif

		isFloating = true
		isDescending = false
		justStoppedDescent = false
		brakePulse = false
		SetFlightFootstepsMuted(true)
		if PlayerRef.IsSneaking()
			PlayerRef.StartSneaking()
		endif
		if ActionPointsAV
			PlayerRef.RestoreValue(ActionPointsAV, 9999.0)
		endif

		if mySession != flightSessionId || jumpHeld || isAscending || isDescending || !isFloating
			return
		endif
		lockedZ = curZ - 1.5
		if !isTimerTicking
			StartTimer(0.025, TIMER_FLOAT)
		endif

		float px = PlayerRef.GetPositionX()
		float py = PlayerRef.GetPositionY()
		curZ = PlayerRef.GetPositionZ()
		if mySession != flightSessionId || jumpHeld || isAscending || isDescending || !isFloating
			return
		endif

		float mvX = px - lastPlayerX
		float mvY = py - lastPlayerY
		float mvSq = (mvX * mvX) + (mvY * mvY)
		float upLeadX = px
		float upLeadY = py
		if mvSq > 0.25
			float mvLen = Math.Sqrt(mvSq)
			upLeadX = px + ((mvX / mvLen) * 64.0)
			upLeadY = py + ((mvY / mvLen) * 64.0)
		elseif platEnabled && !aimBackOffsetActive
			float prevLeadX = lastPlatX - lastRelayPlayerX
			float prevLeadY = lastPlatY - lastRelayPlayerY
			float prevLeadSq = (prevLeadX * prevLeadX) + (prevLeadY * prevLeadY)
			if prevLeadSq > 1.0
				float prevLeadLen = Math.Sqrt(prevLeadSq)
				upLeadX = px + ((prevLeadX / prevLeadLen) * 64.0)
				upLeadY = py + ((prevLeadY / prevLeadLen) * 64.0)
			endif
		endif
		lastPlayerX = px
		lastPlayerY = py
		lastZ = curZ

		; Bloquear altitud directamente bajo las botas actuales (curZ - 1.5 <= curZ):
		; 0 caida libre desde cualquier altura alcanzada con [Y] y 0 colision con CamTarget (curZ + 141).
		lockedZ = curZ - 1.5
		PlaceDualSupport(upLeadX, upLeadY, px, py, lockedZ)
		if mySession != flightSessionId || jumpHeld || isAscending || isDescending || !isFloating
			return
		endif
		float postLockZ = PlayerRef.GetPositionZ()
		if mySession != flightSessionId || jumpHeld || isAscending || isDescending || !isFloating
			return
		endif
		if postLockZ < (lockedZ - 14.0)
			lockedZ = postLockZ - 2.0
			lastZ = postLockZ
			PlaceDualSupport(upLeadX, upLeadY, px, py, lockedZ)
			if mySession != flightSessionId || jumpHeld || isAscending || isDescending || !isFloating
				return
			endif
		endif
		Debug.Trace("[Aero-Mod] HoverLock curZ=" + postLockZ + " lockedZ=" + lockedZ + " PA=" + inPowerArmorCached)

		ApplyFlightAnimState(1)
		if mySession == flightSessionId && !jumpHeld && !isAscending && (isFloating || isDescending) && !isTimerTicking
			StartTimer(0.025, TIMER_FLOAT)
		endif

	elseif control == "Sneak" || control == "Melee"
		if isFloating || isAscending
			forceAuxCheck = true
		endif

	elseif control == "TogglePOV" || control == "ZoomIn"
		if !scopeMenuOpen && !aimHeld
			povTogglePending = true
			if isFloating || isAscending || isDescending
				forceAuxCheck = true
			elseif pending3rdPersonCleanup
				StartTimer(0.15, TIMER_POV_CLEAN)
			endif
		endif
	endif
EndEvent

Event OnKeyDown(int keyCode)
	if Utility.IsInMenuMode()
		return
	endif
	if keyCode == KEY_H
		StopFloating(true)
	endif
EndEvent

Event OnTimer(int aiTimerID)
	if aiTimerID == TIMER_INIT
		SetupFlightSystem(true)

	elseif aiTimerID == TIMER_POST_PIPBOY
		if !PlayerRef
			PlayerRef = Game.GetPlayer()
		endif
		if !PlayerRef
			return
		endif
		if !PlayerRef.Is3DLoaded() || IsPipboyOrMenuBusy()
			StartTimer(0.20, TIMER_POST_PIPBOY)
			return
		endif
		bool didEquipSync = pendingPostPipboySync
		pendingPostPipboySync = false
		RefreshPowerArmorCache()
		RefreshHeroSuitCache()
		RefreshCosmosPACache()
		RefreshHeroWeaponCache()
		RefreshPAWeaponCache()
		EnsureFlightAbilities()
		if isFloating || isAscending
			if !CanPlayerFlyNow()
				Debug.Notification("[Astro-Cosmos] Propulsor desequipado en el aire: descendiendo...")
				StartControlledDescent(false)
				return
			endif
			forceAuxCheck = true
			if PlayerRef.IsWeaponDrawn() && !IsWeaponHolsteringNow() && !IsAllowedFlightWeaponEquipped()
				StartControlledDescent(true)
				return
			endif
			if !PlayerRef.GetAnimationVariableBool("IsFirstPerson") && !IsPlayerAimingOrScoped()
				ApplyFlightAnimState(1)
				if didEquipSync
					PlayerRef.AttemptAnimationSetSwitch()
				endif
			endif
			if !isTimerTicking
				StartTimer(0.025, TIMER_FLOAT)
			endif
		elseif isDescending
			ApplyFlightAnimState(2)
			if !isTimerTicking
				StartTimer(0.03, TIMER_FLOAT)
			endif
		endif

	elseif aiTimerID == TIMER_POV_CLEAN
		if PlayerRef && PlayerRef.Is3DLoaded() && pending3rdPersonCleanup && !isFloating && !isAscending && !isDescending
			if IsPipboyOrMenuBusy()
				StartTimer(0.20, TIMER_POV_CLEAN)
				return
			endif
			if !PlayerRef.GetAnimationVariableBool("IsFirstPerson")
				ExecuteGroundSubgraphReset()
				landSwitchFollowups = 2
				StartTimer(0.20, TIMER_LAND_CLEAN)
			endif
		endif

	elseif aiTimerID == TIMER_LAND_CLEAN
		int cleanSession = flightSessionId
		if !PlayerRef || isFloating || isAscending || isDescending
			pendingGroundFlavorReset = false
			landSwitchFollowups = 0
			return
		endif
		if !PlayerRef.Is3DLoaded() || IsPipboyOrMenuBusy()
			if cleanSession != flightSessionId || isFloating || isAscending || isDescending
				pendingGroundFlavorReset = false
				landSwitchFollowups = 0
				return
			endif
			StartTimer(0.20, TIMER_LAND_CLEAN)
			return
		endif
		if pendingGroundFlavorReset
			landCleanTicks += 1
			if !PlayerRef.GetAnimationVariableBool("IsFirstPerson") && PlayerRef.GetAnimationVariableBool("bInJumpState") && landCleanTicks < 16
				if cleanSession != flightSessionId || isFloating || isAscending || isDescending
					pendingGroundFlavorReset = false
					landSwitchFollowups = 0
					return
				endif
				StartTimer(0.06, TIMER_LAND_CLEAN)
				return
			endif
			if cleanSession != flightSessionId || isFloating || isAscending || isDescending
				pendingGroundFlavorReset = false
				landSwitchFollowups = 0
				return
			endif
			ExecuteGroundSubgraphReset()
			if cleanSession != flightSessionId || isFloating || isAscending || isDescending
				pendingGroundFlavorReset = false
				landSwitchFollowups = 0
				return
			endif
			landSwitchFollowups = 4
			StartTimer(0.20, TIMER_LAND_CLEAN)
			return
		endif
		if landSwitchFollowups > 0
			landSwitchFollowups -= 1
			if PlayerRef.GetAnimationVariableBool("IsFirstPerson") || !PlayerRef.GetAnimationVariableBool("bInLandingState") || landSwitchFollowups == 0
				if cleanSession != flightSessionId || isFloating || isAscending || isDescending
					landSwitchFollowups = 0
					return
				endif
				ClearCustomSubgraphKeywords()
				if cleanSession != flightSessionId || isFloating || isAscending || isDescending
					landSwitchFollowups = 0
					return
				endif
				PlayerRef.ChangeAnimFlavor(None)
			endif
			if cleanSession != flightSessionId || isFloating || isAscending || isDescending
				landSwitchFollowups = 0
				return
			endif
			PlayerRef.AttemptAnimationSetSwitch()
			if PlayerRef.IsSneaking()
				PlayerRef.StartSneaking()
			endif
			if landSwitchFollowups > 0 && cleanSession == flightSessionId && !isFloating && !isAscending && !isDescending
				StartTimer(0.25, TIMER_LAND_CLEAN)
			endif
		endif

	elseif aiTimerID == TIMER_FLOAT
		if isTimerTicking
			return
		endif
		if !isFloating && !isAscending && !isDescending
			return
		endif

		isTimerTicking = true
		int tickSession = flightSessionId

		if !Utility.IsInMenuMode() && PlayerRef
			if !CanPlayerFlyNow() && !isDescending
				StartControlledDescent(false)
				isTimerTicking = false
				return
			endif

			; Lectura minima ultrarrapida (solo 3 llamadas nativas en el bucle caliente)
			float px = PlayerRef.GetPositionX()
			float py = PlayerRef.GetPositionY()
			float curZ = PlayerRef.GetPositionZ()
			if tickSession != flightSessionId || (!isFloating && !isAscending && !isDescending)
				isTimerTicking = false
				if isFloating || isAscending || isDescending
					StartTimer(0.025, TIMER_FLOAT)
				endif
				return
			endif
			float velZ = curZ - lastZ
			float vx = px - lastPlayerX
			float vy = py - lastPlayerY
			lastZ = curZ
			lastPlayerX = px
			lastPlayerY = py

			float spdSq = (vx * vx) + (vy * vy)
			if spdSq < 4.0 && sprintBoostActive
				sprintBoostActive = false
			endif

			; Anticipacion horizontal dinamica (hasta 72 unidades al esprintar con L3 en 3a persona,
			; dejando 200 unidades continuas de losa solida por delante de los pies del jugador)
			float leadX = px
			float leadY = py
			if spdSq > 0.25
				float spdXY = Math.Sqrt(spdSq)
				float leadDist = spdXY * 2.4
				if sprintBoostActive && leadDist < 68.0
					leadDist = 68.0
				endif
				if leadDist > 72.0
					leadDist = 72.0
				endif
				leadX = px + ((vx / spdXY) * leadDist)
				leadY = py + ((vy / spdXY) * leadDist)
			endif

			if isAscending
				climbTicks += 1
				float holdElapsed = Utility.GetCurrentRealTime() - takeoffRealTime

				if ActionPointsAV && (climbTicks % 4) == 0
					PlayerRef.RestoreValue(ActionPointsAV, 9999.0)
					if tickSession != flightSessionId || !jumpHeld || !isAscending || isDescending
						isTimerTicking = false
						if isFloating || isAscending || isDescending
							StartTimer(0.025, TIMER_FLOAT)
						endif
						return
					endif
				endif

				if !isFloating && jumpHeld && (holdElapsed >= 0.16 || climbTicks >= 3 || (curZ - takeoffZ) >= 14.0)
					float preTakeoffX = px
					float preTakeoffY = py
					float preTakeoffZ = curZ
					isFloating = true
					SetFlightFootstepsMuted(true)
					if PlayerRef.IsSneaking()
						PlayerRef.StartSneaking()
					endif
					lockedZ = curZ
					ApplyFlightAnimState(1)
					if tickSession != flightSessionId || !jumpHeld || !isAscending || isDescending
						isTimerTicking = false
						if isFloating || isAscending || isDescending
							StartTimer(0.025, TIMER_FLOAT)
						endif
						return
					endif
					px = PlayerRef.GetPositionX()
					py = PlayerRef.GetPositionY()
					curZ = PlayerRef.GetPositionZ()
					if tickSession != flightSessionId || !jumpHeld || !isAscending || isDescending
						isTimerTicking = false
						if isFloating || isAscending || isDescending
							StartTimer(0.025, TIMER_FLOAT)
						endif
						return
					endif
					leadX = px + (leadX - preTakeoffX)
					leadY = py + (leadY - preTakeoffY)
					float animClimbZ = curZ - preTakeoffZ
					if animClimbZ > velZ
						velZ = animClimbZ
					endif
					lastPlayerX = px
					lastPlayerY = py
					lastZ = curZ
					lockedZ = curZ
					Debug.Trace("[Aero-Mod] TakeoffStart takeoffZ=" + takeoffZ + " curZ=" + curZ + " velZ=" + velZ + " PA=" + inPowerArmorCached)
				endif

				if isFloating
					if forceAuxCheck
						forceAuxCheck = false
						if PlayerRef.IsSneaking()
							PlayerRef.StartSneaking()
						endif
						ApplyFlightAnimState(1)
						if tickSession != flightSessionId || !jumpHeld || !isAscending || isDescending
							isTimerTicking = false
							if isFloating || isAscending || isDescending
								StartTimer(0.025, TIMER_FLOAT)
							endif
							return
						endif
					endif
					; Seguimiento unificado de altura durante la subida con [Y] (Servoarmadura / Traje):
					; - Si el propulsor nativo sube (velZ > ascVelThresh), llevar la losa retrasada bajo
					;   las botas (curZ - ascLag) para no frenar el impulso vertical.
					; - Si sufre una caida brusca manteniendo [Y] (velZ < -10.0), capturar bajo las botas.
					; - Al llegar al apice o frenarse la subida, incrementar lockedZ gradualmente (+ascStep)
					;   acotado a curZ + ascCap para elevar al jugador sin frenar el despegue.
					float ascVelThresh = 4.0
					float ascLag = 12.0
					float ascStep = 8.5
					float ascCap = 10.0
					if inPowerArmorCached
						ascVelThresh = 2.0
						ascLag = 16.0
						ascStep = 6.5
						ascCap = 8.0
					endif
					if velZ > ascVelThresh
						lockedZ = curZ
						AdvancePlatformRelay(leadX, leadY, curZ - ascLag, px, py)
					elseif velZ < -10.0
						lockedZ = curZ + (velZ * 1.5) - 4.0
						PlaceDualSupport(leadX, leadY, px, py, lockedZ)
					else
						lockedZ += ascStep
						if lockedZ > (curZ + ascCap)
							lockedZ = curZ + ascCap
						elseif lockedZ < (curZ - 2.0)
							lockedZ = curZ
						endif
						AdvancePlatformRelay(leadX, leadY, lockedZ, px, py)
					endif
				endif

			elseif isDescending
				climbTicks += 1
				if velZ < -2.0
					hasFallenDuringDescent = true
				endif
				if forceAuxCheck
					forceAuxCheck = false
					ApplyFlightAnimState(2)
					if PlayerRef.IsSneaking()
						PlayerRef.StartSneaking()
					endif
				endif
				if platEnabled
					HidePlatforms()
				endif
				if hasFallenDuringDescent && climbTicks >= 5 && Math.Abs(velZ) < 0.9
					landedTicks += 1
					if landedTicks >= 3
						StopFloating(true)
						isTimerTicking = false
						return
					endif
				elseif !hasFallenDuringDescent && climbTicks >= 16 && Math.Abs(velZ) < 0.5
					landedTicks += 1
					if landedTicks >= 4
						StopFloating(true)
						isTimerTicking = false
						return
					endif
				else
					landedTicks = 0
				endif

			elseif isFloating
				bool didRelayThisTick = false
				if curZ > (lockedZ + 8.0) && velZ >= 0.0
					lockedZ = curZ - 1.5
				endif

				; HoverPlatform usa L_STAIRHELPER (capa Havok 31): solida para el jugador y 100% permeable a proyectiles y VATS LOS en cualquier angulo (0-90 grados), evitando desplazar las losas al apuntar.
				bool wantBackAim = false
				if wantBackAim
					; Al disparar muy picado hacia abajo en vuelo estacionario (> 46 grados), retrasar la losa
					; 68u tras los pies para despejar el angulo de tiro manteniendo 60u de apoyo frontal.
					float aimYaw = PlayerRef.GetAngleZ()
					float backX = px - (Math.sin(aimYaw) * 68.0)
					float backY = py - (Math.cos(aimYaw) * 68.0)
					float bdx = backX - lastPlatX
					float bdy = backY - lastPlatY
					if !aimBackOffsetActive || !platEnabled || ((bdx * bdx) + (bdy * bdy)) > 256.0
						aimBackOffsetActive = true
						PlaceDualSupport(backX, backY, backX, backY, lockedZ)
						didRelayThisTick = true
					endif
				else
					if justStoppedDescent
						justStoppedDescent = false
						aimBackOffsetActive = false
						lockedZ = curZ - 1.5
						PlaceDualSupport(leadX, leadY, px, py, lockedZ)
						didRelayThisTick = true
					elseif curZ < (lockedZ - 18.0) || (curZ < (lockedZ - 9.0) && velZ < -3.5)
						; Compensacion predictiva de velocidad vertical: situar ambas losas por delante de la caida
						; (curZ + velZ * 1.5 - 4.0) para que tras los ~33 ms latentes de SetPosition las botas aterricen
						; sobre una losa estacionaria en vez de atravesarla hacia abajo.
						aimBackOffsetActive = false
						float catchZ = curZ - 2.0
						if velZ < -3.0
							catchZ = curZ + (velZ * 1.5) - 4.0
						endif
						lockedZ = catchZ
						PlaceDualSupport(leadX, leadY, px, py, lockedZ)
						didRelayThisTick = true
					elseif aimBackOffsetActive
						aimBackOffsetActive = false
						PlaceDualSupport(leadX, leadY, px, py, lockedZ)
						didRelayThisTick = true
					elseif !platEnabled
						PlaceDualSupport(leadX, leadY, px, py, lockedZ)
						didRelayThisTick = true
					else
						; Medir desplazamiento REAL del jugador (px - lastRelayPlayerX) y NO contra leadX,
						; para disparar el relevo cada 30u y evitar mover losas en estacionario de 3a persona.
						float dx = px - lastRelayPlayerX
						float dy = py - lastRelayPlayerY
						float distSq = (dx * dx) + (dy * dy)
						if distSq > 900.0
							AdvancePlatformRelay(leadX, leadY, lockedZ, px, py)
							didRelayThisTick = true
						elseif curZ < (lockedZ - 3.5) && spdSq > 16.0 && distSq > 225.0
							; Adelantar relevo antes de 30u solo si el jugador se esta desplazando horizontalmente.
							AdvancePlatformRelay(leadX, leadY, lockedZ, px, py)
							didRelayThisTick = true
						endif
					endif
				endif

				; Comprobaciones secundarias (arma, sigilo, cambio de camara 1a/3a y AP) diferidas fuera
				; de los ticks de relevo o cuando el jugador pulsa TogglePOV/ReadyWeapon, manteniendo
				; el bucle de esprintar en solo 3-4 frames totales (~60 ms).
				auxCheckCounter += 1
				if forceAuxCheck || (!didRelayThisTick && auxCheckCounter >= 8) || auxCheckCounter >= 14
					forceAuxCheck = false
					auxCheckCounter = 0
					if PlayerRef.IsWeaponDrawn() && !IsWeaponHolsteringNow()
						RefreshHeroWeaponCache()
						RefreshPAWeaponCache()
						if !IsAllowedFlightWeaponEquipped()
							StartControlledDescent(true)
							isTimerTicking = false
							return
						endif
					endif
					if PlayerRef.IsSneaking()
						PlayerRef.StartSneaking()
					endif
					ApplyFlightAnimState(1)
					if ActionPointsAV
						PlayerRef.RestoreValue(ActionPointsAV, 9999.0)
					endif
				endif
			endif
		endif

		isTimerTicking = false
		if isFloating || isAscending || isDescending
			StartTimer(0.025, TIMER_FLOAT)
		endif
	endif
EndEvent

Function TriggerCosmicCarbineHit(Actor akTarget, Actor akCaster)
	if akTarget == None || akCaster == None
		return
	endif

	cosmicHitCounter += 1
	EffectShader alienGlow = Game.GetFormFromFile(0x00179639, "Fallout4.esm") as EffectShader
	if alienGlow != None
		alienGlow.Play(akTarget, 1.5)
	endif

	if cosmicHitCounter >= 4 || akTarget.IsDead()
		cosmicHitCounter = 0
		EffectShader shockArcs = Game.GetFormFromFile(0x0006F122, "Fallout4.esm") as EffectShader
		if shockArcs != None
			shockArcs.Play(akTarget, 2.0)
		endif
		Explosion cryoPulse = Game.GetFormFromFile(0x00230F89, "Fallout4.esm") as Explosion
		if cryoPulse != None
			akTarget.PlaceAtMe(cryoPulse, 1, false, false)
		endif

		ActorValue healthAV = Game.GetFormFromFile(0x000002D4, "Fallout4.esm") as ActorValue
		if !akTarget.IsDead()
			akCaster.PushActorAway(akTarget, 3.0)
			if healthAV != None
				akTarget.DamageValue(healthAV, 25.0)
			endif
		endif

		if !PlayerRef
			PlayerRef = Game.GetPlayer()
		endif
		if akCaster == PlayerRef && PlayerRef != None
			if !ActionPointsAV
				ActionPointsAV = Game.GetFormFromFile(0x000002D5, "Fallout4.esm") as ActorValue
			endif
			if ActionPointsAV != None
				PlayerRef.RestoreValue(ActionPointsAV, 25.0)
			endif
			if healthAV != None
				PlayerRef.RestoreValue(healthAV, 15.0)
			endif
			Debug.Notification("[Carabina Astro-Cosmos] Pulso Fotonico Cosmico (+25 PA / +15 PS)")
		endif
	endif
EndFunction

Function TriggerCosmicCannonHit(Actor akTarget, Actor akCaster)
	if akTarget == None || akCaster == None
		return
	endif

	solarCannonHitCounter += 1
	EffectShader shockArcs = Game.GetFormFromFile(0x0006F122, "Fallout4.esm") as EffectShader
	if shockArcs != None
		shockArcs.Play(akTarget, 1.8)
	endif

	if solarCannonHitCounter >= 3 || akTarget.IsDead()
		solarCannonHitCounter = 0
		EffectShader plasmaGlow = Game.GetFormFromFile(0x00179639, "Fallout4.esm") as EffectShader
		if plasmaGlow != None
			plasmaGlow.Play(akTarget, 2.2)
		endif
		Explosion solarPulse = Game.GetFormFromFile(0x00230F89, "Fallout4.esm") as Explosion
		if solarPulse != None
			akTarget.PlaceAtMe(solarPulse, 1, false, false)
		endif

		ActorValue healthAV = Game.GetFormFromFile(0x000002D4, "Fallout4.esm") as ActorValue
		if !akTarget.IsDead()
			akCaster.PushActorAway(akTarget, 5.5)
			if healthAV != None
				akTarget.DamageValue(healthAV, 42.0)
			endif
		endif

		if !PlayerRef
			PlayerRef = Game.GetPlayer()
		endif
		if akCaster == PlayerRef && PlayerRef != None
			if !ActionPointsAV
				ActionPointsAV = Game.GetFormFromFile(0x000002D5, "Fallout4.esm") as ActorValue
			endif
			if ActionPointsAV != None
				PlayerRef.RestoreValue(ActionPointsAV, 35.0)
			endif
			if healthAV != None
				PlayerRef.RestoreValue(healthAV, 25.0)
			endif
			Debug.Notification("[Canon Orbital Astro-Cosmos] Supernova Gravitatoria Solar (+35 PA / +25 PS)")
		endif
	endif
EndFunction

Function ResetPrototypesForCampaignStart()
	if !PlayerRef
		PlayerRef = Game.GetPlayer()
	endif
	if !PlayerRef
		return
	endif
	StopFloating(false)
	Armor suitForm = Game.GetFormFromFile(0x00000800, "AeroArmorMod.esp") as Armor
	if suitForm && PlayerRef.GetItemCount(suitForm) > 0
		if PlayerRef.IsEquipped(suitForm)
			PlayerRef.UnequipItem(suitForm, false, true)
		endif
		PlayerRef.RemoveItem(suitForm, 99, true)
	endif
	Weapon heroWeapForm = Game.GetFormFromFile(0x00000840, "AeroArmorMod.esp") as Weapon
	if heroWeapForm && PlayerRef.GetItemCount(heroWeapForm) > 0
		if PlayerRef.IsEquipped(heroWeapForm)
			PlayerRef.UnequipItem(heroWeapForm, false, true)
		endif
		PlayerRef.RemoveItem(heroWeapForm, 99, true)
	endif
	Weapon paWeapForm = Game.GetFormFromFile(0x00000850, "AeroArmorMod.esp") as Weapon
	if paWeapForm && PlayerRef.GetItemCount(paWeapForm) > 0
		if PlayerRef.IsEquipped(paWeapForm)
			PlayerRef.UnequipItem(paWeapForm, false, true)
		endif
		PlayerRef.RemoveItem(paWeapForm, 99, true)
	endif
	if !PlayerRef.IsInPowerArmor()
		int idx = 0
		while idx < 6
			Armor paPiece = Game.GetFormFromFile(0x00000820 + idx, "AeroArmorMod.esp") as Armor
			if paPiece && PlayerRef.GetItemCount(paPiece) > 0
				PlayerRef.RemoveItem(paPiece, 99, true)
			endif
			idx += 1
		endWhile
	endif
	RefreshPowerArmorCache()
	RefreshHeroSuitCache()
	RefreshCosmosPACache()
	RefreshHeroWeaponCache()
	RefreshPAWeaponCache()
	EnsureFlightAbilities()
EndFunction
