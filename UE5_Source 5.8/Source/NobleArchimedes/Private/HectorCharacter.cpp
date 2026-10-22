// Fill out your copyright notice in the Description page of Project Settings.

#include "HectorCharacter.h"
#include "AnimVariableBridge.h"
#include "NobleArchimedesCameraComponent.h"
#include "NobleArchimedesInnocentDevilComponent.h"
#include "NobleArchimedesItemSystem.h"
#include "NobleArchimedesWeaponForge.h"
#include "NobleArchimedesGameInstance.h"
#include "NobleArchimedesGameModeBase.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "NobleArchimedesPlayerController.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputActionValue.h"
#include "InputMappingContext.h"
#include "InputAction.h"
#include "EnemyBase.h"
#include "ItemDrop.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "TimerManager.h"


AHectorCharacter::AHectorCharacter()
{
	PrimaryActorTick.bCanEverTick = true;

	// Components
	CombatComponent = CreateDefaultSubobject<UNobleArchimedesCombatComponent>(TEXT("CombatComponent"));
	CameraComponent = CreateDefaultSubobject<UNobleArchimedesCameraComponent>(TEXT("CameraComponent"));
	InnocentDevilComponent = CreateDefaultSubobject<UNobleArchimedesInnocentDevilComponent>(TEXT("InnocentDevilComponent"));
	ItemSystem = CreateDefaultSubobject<UNobleArchimedesItemSystem>(TEXT("ItemSystem"));
	WeaponForge = CreateDefaultSubobject<UNobleArchimedesWeaponForge>(TEXT("WeaponForge"));

	// Setup camera boom
	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
	CameraBoom->SetupAttachment(RootComponent);
	CameraBoom->TargetArmLength = 300.0f;
	CameraBoom->bUsePawnControlRotation = true;

	// Camera lag smooths the follow in both position and rotation. Epic's own
	// TP_ThirdPerson template enables both (CameraLagSpeed 8), which is what
	// gives a modern third-person camera its weight; without it the boom snaps
	// rigidly to the character and reads as an old fixed follow cam.
	CameraBoom->bEnableCameraLag = true;
	CameraBoom->CameraLagSpeed = 10.0f;
	CameraBoom->bEnableCameraRotationLag = true;
	CameraBoom->CameraRotationLagSpeed = 12.0f;

	// The collision probe kept jamming the boom against walls and the lock
	// barriers, pinning the camera inside geometry and rendering the screen
	// black. In a tight blockout it is better to clip through architecture than
	// to blind the player, so the probe stays off.
	CameraBoom->bDoCollisionTest = false;

	// Shoulder bias (+Y) and a raised pivot (+Z): the modern over-the-shoulder
	// framing, offset so Hector sits left of centre rather than dead-centre.
	CameraBoom->SocketOffset = FVector(0.0f, 50.0f, 75.0f);

	FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
	FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
	FollowCamera->bUsePawnControlRotation = false;

	// Configure character movement
	GetCharacterMovement()->bOrientRotationToMovement = true;
	GetCharacterMovement()->RotationRate = FRotator(0.0f, 540.0f, 0.0f);
	GetCharacterMovement()->JumpZVelocity = 600.0f;
	GetCharacterMovement()->AirControl = 0.2f;
	// AnimationFrameData.md: Run is the default gait (350 UU/s); Walk is 150.
	GetCharacterMovement()->MaxWalkSpeed = RunSpeed;
}

void AHectorCharacter::BeginPlay()
{
	Super::BeginPlay();

	AddDefaultMappingContext();

	// Two camera components competed for the view target. CameraComponent (the
	// mode camera) only moves when SetInput() is called, and nothing ever called
	// it, so the view stayed frozen and ignored the control rotation entirely --
	// mouse look appeared dead. Keep the boom camera, which follows the pawn's
	// control rotation, and switch the mode camera back on once it is driven.
	if (CameraComponent)
	{
		// Deactivate() alone does not stop a component's tick, so this kept
		// running every frame and overwrote FollowCamera's world transform with
		// its own frozen yaw -- the view snapped back toward the character as
		// soon as the boom moved it. Disable the tick outright.
		CameraComponent->SetComponentTickEnabled(false);
		CameraComponent->SetAutoActivate(false);
		CameraComponent->Deactivate();
	}
	if (FollowCamera)
	{
		FollowCamera->SetActive(true);
	}

	UE_LOG(LogTemp, Display, TEXT("NA-INPUT cameras: mode=%s follow=%s"),
		CameraComponent && CameraComponent->IsActive() ? TEXT("active") : TEXT("inactive"),
		FollowCamera && FollowCamera->IsActive() ? TEXT("active") : TEXT("inactive"));

	// Why this matters: a mesh whose AnimationMode is not AnimationBlueprint, or
	// whose AnimClass fails to instantiate, renders the reference pose and looks
	// exactly like a broken state machine.
	if (USkeletalMeshComponent* MeshComp = GetMesh())
	{
		UE_LOG(LogTemp, Display,
			TEXT("NA-ANIMSTATE mesh=%s skel=%s mode=%d animClass=%s animInstance=%s"),
			*GetNameSafe(MeshComp->GetSkeletalMeshAsset()),
			*GetNameSafe(MeshComp->GetSkeletalMeshAsset() ? MeshComp->GetSkeletalMeshAsset()->GetSkeleton() : nullptr),
			static_cast<int32>(MeshComp->GetAnimationMode()),
			*GetNameSafe(MeshComp->AnimClass),
			*GetNameSafe(MeshComp->GetAnimInstance()));
	}

	UE_LOG(LogTemp, Display,
		TEXT("NobleArchimedes: Hector BeginPlay. Controller=%s MappingContext=%s"),
		*GetNameSafe(GetController()), *GetNameSafe(DefaultMappingContext));

	if (UNobleArchimedesGameInstance* GameInstance = Cast<UNobleArchimedesGameInstance>(GetGameInstance()))
	{
		GameInstance->ApplyPendingLoad();
	}

	if (ANobleArchimedesGameModeBase* GameMode =
		Cast<ANobleArchimedesGameModeBase>(UGameplayStatics::GetGameMode(this)))
	{
		GameMode->ApplyChapterUnlocks(GameMode->GetCurrentChapter());
	}

#if !UE_BUILD_SHIPPING
	if (FParse::Param(FCommandLine::Get(), TEXT("NATestCombat")))
	{
		if (UWorld* World = GetWorld())
		{
			World->GetTimerManager().SetTimerForNextTick(this, &AHectorCharacter::RunCombatSmokeTest);
		}
	}
	if (FParse::Param(FCommandLine::Get(), TEXT("NATestSpawn")))
	{
		if (UWorld* World = GetWorld())
		{
			FTimerHandle Handle;
			World->GetTimerManager().SetTimer(Handle, this, &AHectorCharacter::RunSpawnProbe, 1.5f, false);
		}
	}
#endif
}

#if !UE_BUILD_SHIPPING
void AHectorCharacter::RunSpawnProbe()
{
	// Verifies the two Chapter 1 playtest regressions: that the entrance hall
	// populates its encounter when the player starts already inside the trigger,
	// and that the player is not wedged in geometry at spawn.
	UWorld* World = GetWorld();
	if (!World) return;

	const FVector StartLocation = GetActorLocation();
	int32 EnemyCount = 0;
	TArray<FString> EnemyNames;
	for (TActorIterator<AEnemyBase> It(World); It; ++It)
	{
		++EnemyCount;
		EnemyNames.Add(It->GetClass()->GetName());
	}
	UE_LOG(LogTemp, Display, TEXT("NATEST_SPAWN start=(%.1f, %.1f, %.1f) enemies=%d [%s]"),
		StartLocation.X, StartLocation.Y, StartLocation.Z, EnemyCount,
		*FString::Join(EnemyNames, TEXT(",")));

	// Drive forward input through the same path the player uses, then measure
	// the displacement. A wedged capsule will report near-zero travel.
	const float YawBefore = GetControlRotation().Yaw;
	Move(1.0f, 0.0f);
	FTimerHandle MoveHandle;
	World->GetTimerManager().SetTimer(MoveHandle, FTimerDelegate::CreateWeakLambda(this, [this, StartLocation, YawBefore]()
	{
		MoveInputVector = FVector::ZeroVector;
		const FVector EndLocation = GetActorLocation();
		const float Travelled = FVector::Dist2D(StartLocation, EndLocation);
		const float YawDrift = FMath::Abs(FMath::FindDeltaAngleDegrees(YawBefore, GetControlRotation().Yaw));
		UE_LOG(LogTemp, Display,
			TEXT("NATEST_MOVE travelled=%.1f end=(%.1f, %.1f, %.1f) yaw_drift=%.2f moving=%s"),
			Travelled, EndLocation.X, EndLocation.Y, EndLocation.Z, YawDrift,
			GetCharacterMovement()->Velocity.SizeSquared() > 1.0f ? TEXT("yes") : TEXT("no"));
		UE_LOG(LogTemp, Display, TEXT("NATEST_SPAWN RESULT %s"),
			(Travelled > 100.0f && YawDrift < 1.0f) ? TEXT("PASS") : TEXT("FAIL"));
	}), 1.0f, false);
}
#endif


void AHectorCharacter::AddDefaultMappingContext()
{
	if (bDefaultMappingContextAdded || !DefaultMappingContext)
	{
		return;
	}

	if (const APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (ULocalPlayer* LocalPlayer = PC->GetLocalPlayer())
		{
			if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
				ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(LocalPlayer))
			{
				Subsystem->AddMappingContext(DefaultMappingContext, 0);
				bDefaultMappingContextAdded = true;
			}
		}
	}
}

void AHectorCharacter::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// Apply movement relative to the camera yaw. MoveInputVector.X is forward,
	// MoveInputVector.Y is right.
	if (MoveInputVector.SizeSquared() > 0.0f)
	{
		const FRotator ControlRotation = GetControlRotation();
		const FRotator YawRotation(0.0f, ControlRotation.Yaw, 0.0f);
		const FVector Forward = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
		const FVector Right = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);
		AddMovementInput(Forward, MoveInputVector.X);
		AddMovementInput(Right, MoveInputVector.Y);
	}

	// Drive the anim blueprint's locomotion machine. Its transitions fire on
	// these bools, but nothing ever set them, so the machine never left Idle and
	// the mesh held the reference pose (the T-pose seen in playtests).
	if (UAnimInstance* AnimInstance = GetMesh() ? GetMesh()->GetAnimInstance() : nullptr)
	{
		const float Speed2D = GetVelocity().Size2D();
		const bool bMovingNow = Speed2D > 10.0f;
		const bool bRunningNow = Speed2D > WalkSpeed + 1.0f;
		AnimVariableBridge::SetBool(AnimInstance, TEXT("bIsMoving"), bMovingNow);
		AnimVariableBridge::SetBool(AnimInstance, TEXT("bIsRunning"), bRunningNow);
		AnimVariableBridge::SetBool(AnimInstance, TEXT("bIsIdle"), !bMovingNow);
	}

	// Apply look input. Enhanced Input reports mouse deltas per frame, so the
	// accumulated value must be consumed here; leaving it set made every
	// subsequent tick re-apply the same delta and the camera span.
	if (!LookInputVector.IsNearlyZero())
	{
		AddControllerYawInput(LookInputVector.X);
		AddControllerPitchInput(LookInputVector.Y);
		LookInputVector = FVector::ZeroVector;
	}

	// Frame-rate recorder so playtest stutter can be measured from the log.
	{
		static float PerfAccum = 0.0f;
		static int32 PerfFrames = 0;
		static float PerfWorst = 0.0f;
		PerfAccum += DeltaTime;
		++PerfFrames;
		PerfWorst = FMath::Max(PerfWorst, DeltaTime);
		if (PerfAccum >= 1.0f)
		{
			UE_LOG(LogTemp, Display, TEXT("NA-PERF fps=%.1f avg_ms=%.2f worst_ms=%.2f"),
				PerfFrames / PerfAccum,
				(PerfAccum * 1000.0f) / PerfFrames,
				PerfWorst * 1000.0f);
			PerfAccum = 0.0f;
			PerfFrames = 0;
			PerfWorst = 0.0f;
		}
	}
}

void AHectorCharacter::Input_MoveCompleted()
{
	// Digital keys only fire Triggered while held, so the last value would
	// otherwise persist and walk the character forever.
	MoveInputVector = FVector::ZeroVector;
}

void AHectorCharacter::Input_LookCompleted()
{
	LookInputVector = FVector::ZeroVector;
}


void AHectorCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	AddDefaultMappingContext();

	UEnhancedInputComponent* Input = Cast<UEnhancedInputComponent>(PlayerInputComponent);
	if (!Input)
	{
		return;
	}

	if (MoveAction)
	{
		Input->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AHectorCharacter::Input_Move);
		Input->BindAction(MoveAction, ETriggerEvent::Completed, this, &AHectorCharacter::Input_MoveCompleted);
		Input->BindAction(MoveAction, ETriggerEvent::Canceled, this, &AHectorCharacter::Input_MoveCompleted);
	}
	if (LookAction)
	{
		Input->BindAction(LookAction, ETriggerEvent::Triggered, this, &AHectorCharacter::Input_Look);
		Input->BindAction(LookAction, ETriggerEvent::Completed, this, &AHectorCharacter::Input_LookCompleted);
	}
	if (JumpAction)
	{
		Input->BindAction(JumpAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_JumpStarted);
	}
	if (LightAttackAction)
	{
		Input->BindAction(LightAttackAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_LightAttack);
	}
	if (HeavyAttackAction)
	{
		Input->BindAction(HeavyAttackAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_HeavyAttack);
	}
	if (GuardAction)
	{
		Input->BindAction(GuardAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_GuardStarted);
		Input->BindAction(GuardAction, ETriggerEvent::Completed, this, &AHectorCharacter::Input_GuardCompleted);
	}
	if (DodgeAction)
	{
		Input->BindAction(DodgeAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_Dodge);
	}
	if (InteractAction)
	{
		Input->BindAction(InteractAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_Interact);
	}
	if (SummonDevilAction)
	{
		Input->BindAction(SummonDevilAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_CycleInnocentDevil);
	}
	if (CameraModeAction)
	{
		Input->BindAction(CameraModeAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_ToggleCameraMode);
	}
	if (LockOnAction)
	{
		Input->BindAction(LockOnAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_ToggleLockOn);
	}
	if (MapAction)
	{
		Input->BindAction(MapAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_ToggleMap);
	}
	if (PauseAction)
	{
		Input->BindAction(PauseAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_Pause);
	}
	if (UseItemAction)
	{
		Input->BindAction(UseItemAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_UseItem);
	}
	if (ForgeAction)
	{
		Input->BindAction(ForgeAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_Forge);
	}
	if (QuickSaveAction)
	{
		Input->BindAction(QuickSaveAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_QuickSave);
	}
	if (QuickLoadAction)
	{
		Input->BindAction(QuickLoadAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_QuickLoad);
	}
}

void AHectorCharacter::Input_Move(const FInputActionValue& Value)
{
	const FVector2D Axis = Value.Get<FVector2D>();
	static int32 MoveLogs = 0;
	if (MoveLogs < 5)
	{
		UE_LOG(LogTemp, Display, TEXT("NA-INPUT move x=%.3f y=%.3f"), Axis.X, Axis.Y);
		++MoveLogs;
	}
	Move(Axis.X, Axis.Y);
}

void AHectorCharacter::Input_Look(const FInputActionValue& Value)
{
	const FVector2D Axis = Value.Get<FVector2D>();
	static int32 LookLogs = 0;
	if (LookLogs < 5)
	{
		UE_LOG(LogTemp, Display, TEXT("NA-INPUT look x=%.4f y=%.4f"), Axis.X, Axis.Y);
		++LookLogs;
	}
	Look(Axis.X, Axis.Y);
}

void AHectorCharacter::Input_JumpStarted()
{
	Jump();
}

void AHectorCharacter::Input_LightAttack()
{
	LightAttack();
}

void AHectorCharacter::Input_HeavyAttack()
{
	HeavyAttack();
}

void AHectorCharacter::Input_GuardStarted()
{
	StartGuard();
}

void AHectorCharacter::Input_GuardCompleted()
{
	EndGuard();
}

void AHectorCharacter::Input_Dodge()
{
	const FVector Direction = MoveInputVector.IsNearlyZero() ? GetActorForwardVector() : MoveInputVector;
	QuickStep(Direction);
}

void AHectorCharacter::Input_Interact()
{
	TryInteract();
	OnInteractPressed();
}

bool AHectorCharacter::TryInteract()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return false;
	}

	// Steal from the nearest living, stealable enemy in front of Hector.
	AEnemyBase* BestTarget = nullptr;
	float BestDistanceSq = FMath::Square(320.0f);
	const FVector Forward = GetActorForwardVector();
	for (TActorIterator<AEnemyBase> It(World); It; ++It)
	{
		AEnemyBase* Enemy = *It;
		if (!Enemy || Enemy->bIsDead || !Enemy->CanBeStolenByPlayer())
		{
			continue;
		}

		const FVector ToEnemy = Enemy->GetActorLocation() - GetActorLocation();
		if (FVector::DotProduct(Forward, ToEnemy.GetSafeNormal()) < 0.35f)
		{
			continue;
		}

		const float DistanceSq = ToEnemy.SizeSquared();
		if (DistanceSq < BestDistanceSq)
		{
			BestDistanceSq = DistanceSq;
			BestTarget = Enemy;
		}
	}

	return TryStealFromEnemy(BestTarget);
}

bool AHectorCharacter::TryStealFromEnemy(AEnemyBase* Enemy)
{
	if (!Enemy || Enemy->bIsDead || !Enemy->CanBeStolenByPlayer() || !ItemSystem)
	{
		return false;
	}

	FName StolenItem;
	if (ItemSystem->TrySteal(Enemy, StolenItem))
	{
		ItemSystem->AddItem(StolenItem, 1);
		if (WeaponForge)
		{
			WeaponForge->AddMaterial(StolenItem, 1);
		}
		Enemy->bHasBeenStolenFrom = true;
		Enemy->bIsStealable = false;
		UE_LOG(LogTemp, Log, TEXT("NobleArchimedes: stole %s from %s."),
			*StolenItem.ToString(), *Enemy->EnemyName.ToString());
		return true;
	}

	UE_LOG(LogTemp, Log, TEXT("NobleArchimedes: steal attempt on %s failed."),
		*Enemy->EnemyName.ToString());
	return false;
}

void AHectorCharacter::Input_CycleInnocentDevil()
{
	const TArray<EInnocentDevilType> Unlocked = GetUnlockedInnocentDevils();
	if (Unlocked.Num() == 0)
	{
		return;
	}

	const EInnocentDevilType ActiveType = InnocentDevilComponent
		? InnocentDevilComponent->GetActiveInnocentDevilType()
		: EInnocentDevilType::None;
	const int32 CurrentIndex = Unlocked.IndexOfByKey(ActiveType);
	const int32 NextIndex = (CurrentIndex + 1) % Unlocked.Num();
	SummonInnocentDevil(Unlocked[NextIndex]);
}

void AHectorCharacter::Input_ToggleCameraMode()
{
	if (ANobleArchimedesPlayerController* PC = Cast<ANobleArchimedesPlayerController>(GetController()))
	{
		PC->ToggleCameraMode();
	}
}

void AHectorCharacter::Input_ToggleLockOn()
{
	if (ANobleArchimedesPlayerController* PC = Cast<ANobleArchimedesPlayerController>(GetController()))
	{
		PC->ToggleLockOn();
	}
}

void AHectorCharacter::Input_ToggleMap()
{
	if (ANobleArchimedesPlayerController* PC = Cast<ANobleArchimedesPlayerController>(GetController()))
	{
		PC->OpenMap();
	}
}

void AHectorCharacter::Input_Pause()
{
	if (ANobleArchimedesPlayerController* PC = Cast<ANobleArchimedesPlayerController>(GetController()))
	{
		PC->PauseGame();
	}
}

void AHectorCharacter::Input_UseItem()
{
	if (!ItemSystem)
	{
		return;
	}

	// R uses a Potion, then a High Potion if no Potion remains. Both are
	// consumed through the shared item system so HUD and save data stay in sync.
	if (ItemSystem->UseItem("Potion", this))
	{
		UE_LOG(LogTemp, Log, TEXT("NobleArchimedes: used Potion. Health=%.1f."), GetHealth());
	}
	else if (ItemSystem->UseItem("High Potion", this))
	{
		UE_LOG(LogTemp, Log, TEXT("NobleArchimedes: used High Potion. Health=%.1f."), GetHealth());
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("NobleArchimedes: no healing item available."));
	}
}

void AHectorCharacter::Input_Forge()
{
	ForgeBestAvailable();
}

bool AHectorCharacter::ForgeBestAvailable()
{
	if (!WeaponForge)
	{
		return false;
	}

	TArray<FWeaponRecipe> Recipes = WeaponForge->GetAllRecipes();
	Recipes.Sort([](const FWeaponRecipe& A, const FWeaponRecipe& B)
	{
		return A.ForgeLevel < B.ForgeLevel;
	});

	for (const FWeaponRecipe& Recipe : Recipes)
	{
		FName ForgedWeapon;
		if (WeaponForge->ForgeWeaponByName(Recipe.WeaponName, ForgedWeapon))
		{
			if (CombatComponent)
			{
				TArray<FString> Equipped = CombatComponent->GetEquippedWeapons();
				Equipped.AddUnique(ForgedWeapon.ToString());
				CombatComponent->SetEquippedWeapons(Equipped);
				CombatComponent->EquipWeaponByName(ForgedWeapon);
			}
			UE_LOG(LogTemp, Log, TEXT("NobleArchimedes: forged %s."), *ForgedWeapon.ToString());
			return true;
		}
	}

	UE_LOG(LogTemp, Warning, TEXT("NobleArchimedes: not enough materials to forge a weapon."));
	return false;
}

void AHectorCharacter::Input_QuickSave()
{
	if (UNobleArchimedesGameInstance* GameInstance = Cast<UNobleArchimedesGameInstance>(GetGameInstance()))
	{
		GameInstance->SaveGame(0);
		UE_LOG(LogTemp, Log, TEXT("NobleArchimedes: quick-saved to slot 0."));
	}
}

void AHectorCharacter::Input_QuickLoad()
{
	if (UNobleArchimedesGameInstance* GameInstance = Cast<UNobleArchimedesGameInstance>(GetGameInstance()))
	{
		if (GameInstance->HasSaveGame(5))
		{
			GameInstance->LoadGame(5);
			UE_LOG(LogTemp, Log, TEXT("NobleArchimedes: loading autosave slot 5."));
		}
		else if (GameInstance->HasSaveGame(0))
		{
			GameInstance->LoadGame(0);
			UE_LOG(LogTemp, Log, TEXT("NobleArchimedes: loading quick-save slot 0."));
		}
		else
		{
			UE_LOG(LogTemp, Warning, TEXT("NobleArchimedes: no save game to load."));
		}
	}
}

void AHectorCharacter::HandleDeath()
{
	if (bIsDead)
	{
		return;
	}

	bIsDead = true;
	UE_LOG(LogTemp, Warning, TEXT("NobleArchimedes: Hector died; reloading the current chapter."));

	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		DisableInput(PC);
	}

	if (UWorld* World = GetWorld())
	{
		FTimerHandle RespawnTimer;
		FTimerDelegate RespawnDelegate = FTimerDelegate::CreateWeakLambda(this, [this]()
		{
			if (UWorld* CurrentWorld = GetWorld())
			{
				UGameplayStatics::OpenLevel(this, FName(*CurrentWorld->GetMapName()));
			}
		});
		World->GetTimerManager().SetTimer(RespawnTimer, RespawnDelegate, 2.5f, false);
	}
}

void AHectorCharacter::RunCombatSmokeTest()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	FActorSpawnParameters SpawnParams;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	const FVector SpawnLocation = GetActorLocation() + GetActorForwardVector() * 140.0f + FVector(0.0f, 0.0f, 10.0f);
	AEnemyBase* TestEnemy = World->SpawnActor<AEnemyBase>(
		AEnemyBase::StaticClass(), SpawnLocation, GetActorRotation(), SpawnParams);
	if (!TestEnemy)
	{
		UE_LOG(LogTemp, Error, TEXT("NA-TEST: failed to spawn test enemy."));
		return;
	}

	TestEnemy->EnemyName = "Test Skeleton";
	TestEnemy->MaxHealth = 30.0f;
	TestEnemy->Health = 30.0f;
	TestEnemy->CurrentHealth = 30.0f;
	TestEnemy->ItemDrops = "Bone Shard";
	TestEnemy->CanBeStolen = true;
	TestEnemy->StealItem = "Bone Shard";
	TestEnemy->DetectionRange = 0.0f;
	TestEnemy->AttackCooldown = 999.0f;
	TestEnemy->ItemDropClass = LoadClass<AItemDrop>(nullptr, TEXT("/Game/Blueprints/World/BP_ItemDrop.BP_ItemDrop_C"));

	UE_LOG(LogTemp, Log, TEXT("NA-TEST: spawned enemy at %s with %.0f HP."),
		*SpawnLocation.ToString(), TestEnemy->CurrentHealth);

	FTimerHandle FirstAttackTimer;
	World->GetTimerManager().SetTimer(FirstAttackTimer, FTimerDelegate::CreateWeakLambda(this, [this]()
	{
		UE_LOG(LogTemp, Log, TEXT("NA-TEST: light attack 1."));
		LightAttack();
	}), 0.3f, false);

	FTimerHandle SecondAttackTimer;
	World->GetTimerManager().SetTimer(SecondAttackTimer, FTimerDelegate::CreateWeakLambda(this, [this]()
	{
		UE_LOG(LogTemp, Log, TEXT("NA-TEST: light attack 2."));
		LightAttack();
	}), 1.0f, false);

	FTimerHandle ReportTimer;
	World->GetTimerManager().SetTimer(ReportTimer, FTimerDelegate::CreateWeakLambda(this, [this, TestEnemy]()
	{
		if (IsValid(TestEnemy))
		{
			UE_LOG(LogTemp, Log, TEXT("NA-TEST: enemy hp=%.1f dead=%s."),
				TestEnemy->CurrentHealth, TestEnemy->bIsDead ? TEXT("true") : TEXT("false"));
		}
		else
		{
			UE_LOG(LogTemp, Log, TEXT("NA-TEST: enemy was destroyed."));
		}

		int32 DropCount = 0;
		for (TActorIterator<AItemDrop> It(GetWorld()); It; ++It)
		{
			++DropCount;
		}
		UE_LOG(LogTemp, Log, TEXT("NA-TEST: item drops in world=%d."), DropCount);

		SummonInnocentDevil(EInnocentDevilType::Fairy);
		const EInnocentDevilType ActiveType = InnocentDevilComponent
			? InnocentDevilComponent->GetActiveInnocentDevilType()
			: EInnocentDevilType::None;
		UE_LOG(LogTemp, Log, TEXT("NA-TEST: active innocent devil=%d."), static_cast<int32>(ActiveType));

		ApplyDamage(10.0f, EDamageType::Slash);
		UE_LOG(LogTemp, Log, TEXT("NA-TEST: player hp after 10 damage=%.1f."), GetHealth());

		if (WeaponForge)
		{
			WeaponForge->AddMaterial(TEXT("Iron Shard"), 1);
			UE_LOG(LogTemp, Log, TEXT("NA-TEST: forge iron=%d."), WeaponForge->GetMaterialQuantity(TEXT("Iron Shard")));
			const bool bForged = ForgeBestAvailable();
			UE_LOG(LogTemp, Log, TEXT("NA-TEST: forge success=%s forged=%d."),
				bForged ? TEXT("true") : TEXT("false"), GetForgedWeapons().Num());
		}

		if (ItemSystem)
		{
			ItemSystem->AddItem(TEXT("Potion"), 1);
			SetHealth(GetHealth() - 20.0f);
			const bool bUsed = ItemSystem->UseItem(TEXT("Potion"), this);
			UE_LOG(LogTemp, Log, TEXT("NA-TEST: potion used=%s hp=%.1f."),
				bUsed ? TEXT("true") : TEXT("false"), GetHealth());
		}

		if (UNobleArchimedesGameInstance* GameInstance = Cast<UNobleArchimedesGameInstance>(GetGameInstance()))
		{
			GameInstance->SaveGame(4);
			SetHealth(42.0f);
			GameInstance->LoadGame(4);
			UE_LOG(LogTemp, Log, TEXT("NA-TEST: save-load hp=%.1f forged=%d."),
				GetHealth(), GetForgedWeapons().Num());
		}
	}), 2.0f, false);

	FTimerHandle AiSpawnTimer;
	World->GetTimerManager().SetTimer(AiSpawnTimer, FTimerDelegate::CreateWeakLambda(this, [this]()
	{
		UWorld* CurrentWorld = GetWorld();
		if (!CurrentWorld)
		{
			return;
		}

		FActorSpawnParameters AiSpawnParams;
		AiSpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		const FVector AiLocation = GetActorLocation() + GetActorForwardVector() * 650.0f;
		AEnemyBase* Chaser = CurrentWorld->SpawnActor<AEnemyBase>(
			AEnemyBase::StaticClass(), AiLocation, GetActorRotation(), AiSpawnParams);
		if (!Chaser)
		{
			UE_LOG(LogTemp, Error, TEXT("NA-TEST: failed to spawn chasing enemy."));
			return;
		}

		Chaser->EnemyName = "Test Chaser";
		Chaser->MaxHealth = 1000.0f;
		Chaser->CurrentHealth = 1000.0f;
		Chaser->Damage = 5.0f;
		Chaser->AttackRange = 150.0f;
		Chaser->DetectionRange = 1000.0f;
		Chaser->AttackCooldown = 0.5f;
		Chaser->AttackWindup = 0.2f;
		Chaser->ItemDrops = "";
		UE_LOG(LogTemp, Log, TEXT("NA-TEST: chaser spawned; distance=%.0f."),
			FVector::Dist(GetActorLocation(), AiLocation));

		FTimerHandle AiReportTimer;
		CurrentWorld->GetTimerManager().SetTimer(AiReportTimer, FTimerDelegate::CreateWeakLambda(this, [this, Chaser]()
		{
			if (IsValid(Chaser))
			{
				UE_LOG(LogTemp, Log, TEXT("NA-TEST: chaser distance=%.0f player hp=%.1f."),
					FVector::Dist(GetActorLocation(), Chaser->GetActorLocation()), GetHealth());
				Chaser->Destroy();
			}
			else
			{
				UE_LOG(LogTemp, Log, TEXT("NA-TEST: chaser invalid, player hp=%.1f."), GetHealth());
			}
		}), 3.5f, false);
	}), 2.5f, false);
}

void AHectorCharacter::Move(float ValueX, float ValueY)
{
	MoveInputVector = FVector(ValueY, ValueX, 0.0f);
	MoveInputVector.Normalize();
}

void AHectorCharacter::Look(float ValueX, float ValueY)
{
	LookInputVector = FVector(ValueX, ValueY, 0.0f);
}

void AHectorCharacter::SetWalkMode(bool bInWalking)
{
	bWalking = bInWalking;
	if (UCharacterMovementComponent* Movement = GetCharacterMovement())
	{
		Movement->MaxWalkSpeed = bWalking ? WalkSpeed : RunSpeed;
	}
}

void AHectorCharacter::SetCameraMode(ECameraMode NewMode)
{
	// The mode camera no longer drives the view (its tick is disabled), so the
	// camera modes now adjust the spring arm instead of doing nothing.
	// Modern over-the-shoulder framing: closer than the old 350 boom, with a
	// lateral shoulder bias so the character sits off-centre.
	float ArmLength = 300.0f;
	float FOV = 90.0f;
	FVector SocketOffset(0.0f, 50.0f, 75.0f);

	switch (NewMode)
	{
	case ECameraMode::Classic:
		break;
	case ECameraMode::ActionOrbit:
		ArmLength = 420.0f;
		FOV = 85.0f;
		SocketOffset = FVector(0.0f, 0.0f, 120.0f);
		break;
	case ECameraMode::OverTheShoulder:
		ArmLength = 180.0f;
		FOV = 80.0f;
		SocketOffset = FVector(0.0f, 70.0f, 80.0f);
		break;
	}

	if (CameraComponent)
	{
		CameraComponent->SetMode(NewMode);
	}
	if (CameraBoom)
	{
		CameraBoom->TargetArmLength = ArmLength;
		CameraBoom->SocketOffset = SocketOffset;
	}
	if (FollowCamera)
	{
		FollowCamera->SetFieldOfView(FOV);
	}

	UE_LOG(LogTemp, Display, TEXT("NA-INPUT camera mode=%d arm=%.0f fov=%.0f"),
		static_cast<int32>(NewMode), ArmLength, FOV);
}

ECameraMode AHectorCharacter::GetCameraMode() const
{
	return CameraComponent ? CameraComponent->GetMode() : ECameraMode::Classic;
}

void AHectorCharacter::SummonInnocentDevil(EInnocentDevilType Type)
{
	if (InnocentDevilComponent)
	{
		InnocentDevilComponent->SummonInnocentDevil(Type);
	}
}

void AHectorCharacter::SetInnocentDevilMode(EInnocentDevilMode Mode)
{
	if (InnocentDevilComponent)
	{
		InnocentDevilComponent->SetMode(Mode);
	}
}

TArray<FInnocentDevilData> AHectorCharacter::GetInnocentDevils() const
{
	return InnocentDevilComponent ? InnocentDevilComponent->GetInnocentDevils() : TArray<FInnocentDevilData>();
}

int32 AHectorCharacter::GetActiveInnocentDevilIndex() const
{
	if (!InnocentDevilComponent) return 0;

	const TArray<FInnocentDevilData>& Devils = InnocentDevilComponent->GetInnocentDevils();
	EInnocentDevilType ActiveType = InnocentDevilComponent->GetActiveInnocentDevilType();

	for (int32 i = 0; i < Devils.Num(); ++i)
	{
		if (Devils[i].DevilType == ActiveType)
		{
			return i;
		}
	}
	return 0;
}

TArray<EInnocentDevilType> AHectorCharacter::GetUnlockedInnocentDevils() const
{
	TArray<EInnocentDevilType> UnlockedTypes;
	if (!InnocentDevilComponent) return UnlockedTypes;

	const TArray<FInnocentDevilData>& Devils = InnocentDevilComponent->GetInnocentDevils();
	for (const auto& Devil : Devils)
	{
		if (Devil.bIsUnlocked)
		{
			UnlockedTypes.Add(Devil.DevilType);
		}
	}
	return UnlockedTypes;
}

TArray<FName> AHectorCharacter::GetDiscoveredRecipes() const
{
	return WeaponForge ? WeaponForge->GetDiscoveredRecipes() : TArray<FName>();
}

TArray<FName> AHectorCharacter::GetForgedWeapons() const
{
	return WeaponForge ? WeaponForge->GetForgedWeapons() : TArray<FName>();
}

float AHectorCharacter::GetMasterVolume() const
{
	// Default volume; to be wired to an audio settings system when available.
	return 1.0f;
}

float AHectorCharacter::GetSFXVolume() const
{
	return 1.0f;
}

float AHectorCharacter::GetMusicVolume() const
{
	return 0.0f;
}

UNobleArchimedesItemSystem* AHectorCharacter::GetItemSystem() const
{
	return ItemSystem;
}

void AHectorCharacter::SetActiveInnocentDevilIndex(int32 NewIndex)
{
	if (InnocentDevilComponent)
	{
		const TArray<FInnocentDevilData> Devils = InnocentDevilComponent->GetInnocentDevils();
		if (Devils.IsValidIndex(NewIndex) && Devils[NewIndex].bIsUnlocked)
		{
			InnocentDevilComponent->SummonInnocentDevil(Devils[NewIndex].DevilType);
		}
	}
}

void AHectorCharacter::SetUnlockedInnocentDevils(TArray<EInnocentDevilType> NewUnlocked)
{
	if (!InnocentDevilComponent)
	{
		return;
	}

	TArray<FInnocentDevilData> Devils = InnocentDevilComponent->GetInnocentDevils();
	for (FInnocentDevilData& Devil : Devils)
	{
		Devil.bIsUnlocked = NewUnlocked.Contains(Devil.DevilType);
	}
	InnocentDevilComponent->SetInnocentDevils(Devils);
}

void AHectorCharacter::SetInnocentDevils(const TArray<FInnocentDevilData>& NewDevils)
{
	if (InnocentDevilComponent)
	{
		InnocentDevilComponent->SetInnocentDevils(NewDevils);
	}
}

void AHectorCharacter::SetDiscoveredRecipes(TArray<FName> NewRecipes)
{
	if (WeaponForge)
	{
		WeaponForge->SetDiscoveredRecipes(NewRecipes);
	}
}

void AHectorCharacter::SetForgedWeapons(TArray<FName> NewWeapons)
{
	if (WeaponForge)
	{
		WeaponForge->SetForgedWeapons(NewWeapons);
	}
}