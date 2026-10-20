// Fill out your copyright notice in the Description page of Project Settings.

#include "HectorCharacter.h"
#include "NobleArchimedesCameraComponent.h"
#include "NobleArchimedesInnocentDevilComponent.h"
#include "NobleArchimedesItemSystem.h"
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


AHectorCharacter::AHectorCharacter()
{
	PrimaryActorTick.bCanEverTick = true;

	// Components
	CombatComponent = CreateDefaultSubobject<UNobleArchimedesCombatComponent>(TEXT("CombatComponent"));
	CameraComponent = CreateDefaultSubobject<UNobleArchimedesCameraComponent>(TEXT("CameraComponent"));
	InnocentDevilComponent = CreateDefaultSubobject<UNobleArchimedesInnocentDevilComponent>(TEXT("InnocentDevilComponent"));
	ItemSystem = CreateDefaultSubobject<UNobleArchimedesItemSystem>(TEXT("ItemSystem"));

	// Setup camera boom
	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
	CameraBoom->SetupAttachment(RootComponent);
	CameraBoom->TargetArmLength = 400.0f;
	CameraBoom->bUsePawnControlRotation = true;

	FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
	FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
	FollowCamera->bUsePawnControlRotation = false;

	// Configure character movement
	GetCharacterMovement()->bOrientRotationToMovement = true;
	GetCharacterMovement()->RotationRate = FRotator(0.0f, 540.0f, 0.0f);
	GetCharacterMovement()->JumpZVelocity = 600.0f;
	GetCharacterMovement()->AirControl = 0.2f;
}

void AHectorCharacter::BeginPlay()
{
	Super::BeginPlay();

	AddDefaultMappingContext();
	UE_LOG(LogTemp, Display,
		TEXT("NobleArchimedes: Hector BeginPlay. Controller=%s MappingContext=%s"),
		*GetNameSafe(GetController()), *GetNameSafe(DefaultMappingContext));
}

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

	// Apply look input
	if (LookInputVector.SizeSquared() > 0.0f)
	{
		AddControllerYawInput(LookInputVector.X);
		AddControllerPitchInput(LookInputVector.Y);
	}
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
	}
	if (LookAction)
	{
		Input->BindAction(LookAction, ETriggerEvent::Triggered, this, &AHectorCharacter::Input_Look);
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
	if (MapAction)
	{
		Input->BindAction(MapAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_ToggleMap);
	}
	if (PauseAction)
	{
		Input->BindAction(PauseAction, ETriggerEvent::Started, this, &AHectorCharacter::Input_Pause);
	}
}

void AHectorCharacter::Input_Move(const FInputActionValue& Value)
{
	const FVector2D Axis = Value.Get<FVector2D>();
	Move(Axis.X, Axis.Y);
}

void AHectorCharacter::Input_Look(const FInputActionValue& Value)
{
	const FVector2D Axis = Value.Get<FVector2D>();
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
	OnInteractPressed();
}

void AHectorCharacter::Input_CycleInnocentDevil()
{
	const TArray<EInnocentDevilType> Unlocked = GetUnlockedInnocentDevils();
	if (Unlocked.Num() == 0)
	{
		return;
	}

	const int32 NextIndex = (GetActiveInnocentDevilIndex() + 1) % Unlocked.Num();
	SummonInnocentDevil(Unlocked[NextIndex]);
}

void AHectorCharacter::Input_ToggleCameraMode()
{
	if (ANobleArchimedesPlayerController* PC = Cast<ANobleArchimedesPlayerController>(GetController()))
	{
		PC->ToggleCameraMode();
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

void AHectorCharacter::Move(float ValueX, float ValueY)
{
	MoveInputVector = FVector(ValueY, ValueX, 0.0f);
	MoveInputVector.Normalize();
}

void AHectorCharacter::Look(float ValueX, float ValueY)
{
	LookInputVector = FVector(ValueX, ValueY, 0.0f);
}

void AHectorCharacter::SetCameraMode(ECameraMode NewMode)
{
	if (CameraComponent)
	{
		CameraComponent->SetMode(NewMode);
	}
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
	// No WeaponForge component on Hector; return empty. Populate when WeaponForge is integrated.
	return TArray<FName>();
}

TArray<FName> AHectorCharacter::GetForgedWeapons() const
{
	// No WeaponForge component on Hector; return empty. Populate when WeaponForge is integrated.
	return TArray<FName>();
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
		// Implementation would set active devil on the component
		// Stored via InnocentDevilComponent's internal state
	}
}

void AHectorCharacter::SetUnlockedInnocentDevils(TArray<EInnocentDevilType> NewUnlocked)
{
	// Unlocked devils are tracked via InnocentDevilComponent's bIsUnlocked flags on each devil
	// This setter is provided for save/load completeness
}

void AHectorCharacter::SetDiscoveredRecipes(TArray<FName> NewRecipes)
{
	// Discovered recipes tracked via WeaponForge component when integrated
}

void AHectorCharacter::SetForgedWeapons(TArray<FName> NewWeapons)
{
	// Forged weapons tracked via WeaponForge component when integrated
}