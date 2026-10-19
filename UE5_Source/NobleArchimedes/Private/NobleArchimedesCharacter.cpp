// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesCharacter.h"
#include "NobleArchimedesCameraComponent.h"
#include "NobleArchimedesCompanionComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystem.h"

ANobleArchimedesCharacter::ANobleArchimedesCharacter()
{
	PrimaryActorTick.bCanEverTick = true;

	// Components
	CombatComponent = CreateDefaultSubobject<UNobleArchimedesCombatComponent>(TEXT("CombatComponent"));
	CameraComponent = CreateDefaultSubobject<UNobleArchimedesCameraComponent>(TEXT("CameraComponent"));
	CompanionComponent = CreateDefaultSubobject<UNobleArchimedesCompanionComponent>(TEXT("CompanionComponent"));

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

void ANobleArchimedesCharacter::BeginPlay()
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

void ANobleArchimedesCharacter::Tick(float DeltaTime)
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

void ANobleArchimedesCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	if (UEnhancedInputComponent* EnhancedInput = Cast<UEnhancedInputComponent>(PlayerInputComponent))
	{
		// Input actions would be bound here in Blueprint
		// Example structure:
		// EnhancedInput->BindAction(IA_Move, ETriggerEvent::Triggered, this, &ANobleArchimedesCharacter::Move);
	}
}

void ANobleArchimedesCharacter::Move(float ValueX, float ValueY)
{
	MoveInputVector = FVector(ValueY, ValueX, 0.0f);
	MoveInputVector.Normalize();
}

void ANobleArchimedesCharacter::Look(float ValueX, float ValueY)
{
	LookInputVector = FVector(ValueX, ValueY, 0.0f);
}

void ANobleArchimedesCharacter::SetCameraMode(ECameraMode NewMode)
{
	if (CameraComponent)
	{
		CameraComponent->SetMode(NewMode);
	}
}

ECameraMode ANobleArchimedesCharacter::GetCameraMode() const
{
	return CameraComponent ? CameraComponent->GetMode() : ECameraMode::Classic;
}

void ANobleArchimedesCharacter::SummonCompanion(ECompanionType Type)
{
	if (CompanionComponent)
	{
		CompanionComponent->SummonCompanion(Type);
	}
}

void ANobleArchimedesCharacter::SetCompanionMode(ECompanionMode Mode)
{
	if (CompanionComponent)
	{
		CompanionComponent->SetMode(Mode);
	}
}

TArray<FCompanionData> ANobleArchimedesCharacter::GetCompanions() const
{
	return CompanionComponent ? CompanionComponent->GetCompanions() : TArray<FCompanionData>();
}