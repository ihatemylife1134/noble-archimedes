// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesPlayerController.h"
#include "HectorCharacter.h"
#include "EnemyBase.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/GameModeBase.h"
#include "Camera/PlayerCameraManager.h"
#include "EngineUtils.h"
#include "EnhancedInputComponent.h"

ANobleArchimedesPlayerController::ANobleArchimedesPlayerController()
{
	bShowMouseCursor = false;
	bEnableClickEvents = false;
	bEnableTouchEvents = false;
}

void ANobleArchimedesPlayerController::BeginPlay()
{
	Super::BeginPlay();
	CacheHectorCharacter();
}

void ANobleArchimedesPlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();
}

void ANobleArchimedesPlayerController::PauseGame()
{
	if (GetWorld())
	{
		UGameplayStatics::SetGamePaused(GetWorld(), true);
	}
}

void ANobleArchimedesPlayerController::OpenMap()
{
	// Open map UI widget
}

void ANobleArchimedesPlayerController::ToggleCameraMode()
{
	if (AHectorCharacter* Hector = GetHectorCharacter())
	{
		// Camera mode toggle is handled in HectorCharacter
	}
}

void ANobleArchimedesPlayerController::UseStealFocus()
{
	if (AHectorCharacter* Hector = GetHectorCharacter())
	{
		if (AEnemyBase* Target = LockedTarget.Get())
		{
			if (!Target->bIsDead && Target->CanBeStolenByPlayer())
			{
				Hector->TryStealFromEnemy(Target);
				return;
			}
		}

		// No usable lock target: fall back to the nearest stealable enemy.
		Hector->TryInteract();
	}
}

void ANobleArchimedesPlayerController::ToggleLockOn()
{
	if (bLockOnActive)
	{
		ClearLockOn();
		return;
	}

	AHectorCharacter* Hector = GetHectorCharacter();
	if (!Hector)
	{
		return;
	}

	const FVector Origin = Hector->GetActorLocation();
	const FVector ViewDirection = GetControlRotation().Vector();
	float BestScore = FMath::Square(1800.0f);
	AEnemyBase* BestTarget = nullptr;

	for (TActorIterator<AEnemyBase> It(GetWorld()); It; ++It)
	{
		AEnemyBase* Enemy = *It;
		if (!Enemy || Enemy->bIsDead)
		{
			continue;
		}

		const FVector ToEnemy = Enemy->GetActorLocation() - Origin;
		const float DistanceSq = ToEnemy.SizeSquared();
		if (DistanceSq > FMath::Square(1800.0f))
		{
			continue;
		}

		const float Facing = FVector::DotProduct(ViewDirection, ToEnemy.GetSafeNormal());
		if (Facing < -0.25f)
		{
			continue;
		}

		// Prefer close enemies that are near the center of the view.
		const float Score = DistanceSq * (2.0f - Facing);
		if (Score < BestScore)
		{
			BestScore = Score;
			BestTarget = Enemy;
		}
	}

	if (BestTarget)
	{
		LockedTarget = BestTarget;
		bLockOnActive = true;
		UE_LOG(LogTemp, Log, TEXT("NobleArchimedes: lock-on target %s."),
			*BestTarget->EnemyName.ToString());
	}
}

void ANobleArchimedesPlayerController::PlayerTick(float DeltaTime)
{
	Super::PlayerTick(DeltaTime);

	if (!bLockOnActive)
	{
		return;
	}

	AEnemyBase* Target = LockedTarget.Get();
	if (!Target || Target->bIsDead)
	{
		ClearLockOn();
		return;
	}

	if (APlayerCameraManager* CameraManager = PlayerCameraManager)
	{
		const FVector TargetPoint = Target->GetActorLocation() + FVector(0.0f, 0.0f, 40.0f);
		const FRotator DesiredRotation =
			(TargetPoint - CameraManager->GetCameraLocation()).Rotation();
		SetControlRotation(FMath::RInterpTo(
			GetControlRotation(),
			FRotator(DesiredRotation.Pitch, DesiredRotation.Yaw, 0.0f),
			DeltaTime,
			10.0f));
	}
}

void ANobleArchimedesPlayerController::ClearLockOn()
{
	LockedTarget.Reset();
	bLockOnActive = false;
}

AHectorCharacter* ANobleArchimedesPlayerController::GetHectorCharacter() const
{
	if (!CachedHectorCharacter)
	{
		CachedHectorCharacter = Cast<AHectorCharacter>(GetPawn());
	}
	return CachedHectorCharacter;
}

void ANobleArchimedesPlayerController::CacheHectorCharacter()
{
	CachedHectorCharacter = Cast<AHectorCharacter>(GetPawn());
}