// Fill out your copyright notice in the Description page of Project Settings.

#include "HectorCharacter.h"
#include "NobleArchimedesCameraComponent.h"
#include "NobleArchimedesInnocentDevilComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystem.h"

AHectorCharacter::AHectorCharacter()
{
	PrimaryActorTick.bCanEverTick = true;

	// Components
	CombatComponent = CreateDefaultSubobject<UNobleArchimedesCombatComponent>(TEXT("CombatComponent"));
	CameraComponent = CreateDefaultSubobject<UNobleArchimedesCameraComponent>(TEXT("CameraComponent"));
	InnocentDevilComponent = CreateDefaultSubobject<UNobleArchimedesInnocentDevilComponent>(TEXT("InnocentDevilComponent"));

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

	if (UEnhancedInputComponent* EnhancedInput = Cast<UEnhancedInputComponent>(PlayerInputComponent))
	{
		// Input actions would be bound here in Blueprint
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