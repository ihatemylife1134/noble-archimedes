// Fill out your copyright notice in the Description page of Project Settings.

#include "HectorCharacter.h"
#include "NobleArchimedesCameraComponent.h"
#include "NobleArchimedesInnocentDevilComponent.h"
#include "NobleArchimedesItemSystem.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/LocalPlayer.h"


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

	// Setup enhanced input subsystem
	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
		{
			// Input mapping context would be added here in Blueprint
		}
	}
}

void AHectorCharacter::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// Apply movement
	if (MoveInputVector.SizeSquared() > 0.0f)
	{
		AddMovementInput(MoveInputVector, 1.0f);
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