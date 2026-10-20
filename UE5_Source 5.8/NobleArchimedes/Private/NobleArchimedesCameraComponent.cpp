// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesCameraComponent.h"
#include "GameFramework/Character.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Kismet/KismetMathLibrary.h"

UNobleArchimedesCameraComponent::UNobleArchimedesCameraComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void UNobleArchimedesCameraComponent::BeginPlay()
{
	Super::BeginPlay();

	if (AActor* Owner = GetOwner())
	{
		TargetActor = Owner;
	}
}

void UNobleArchimedesCameraComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	UpdateCamera(DeltaTime);
}

void UNobleArchimedesCameraComponent::SetMode(ECameraMode NewMode)
{
	CurrentMode = NewMode;

	switch (CurrentMode)
	{
	case ECameraMode::Classic:
		TargetDistance = ClassicDistance;
		TargetFOV = ClassicFOV;
		break;
	case ECameraMode::ActionOrbit:
		TargetDistance = ActionOrbitDistance;
		TargetFOV = ActionOrbitFOV;
		break;
	case ECameraMode::OverTheShoulder:
		TargetDistance = OverTheShoulderDistance;
		TargetFOV = OverTheShoulderFOV;
		break;
	}
}

void UNobleArchimedesCameraComponent::ToggleMode()
{
	switch (CurrentMode)
	{
	case ECameraMode::Classic:
		SetMode(ECameraMode::ActionOrbit);
		break;
	case ECameraMode::ActionOrbit:
		SetMode(ECameraMode::OverTheShoulder);
		break;
	case ECameraMode::OverTheShoulder:
		SetMode(ECameraMode::Classic);
		break;
	}
}

void UNobleArchimedesCameraComponent::SetTarget(AActor* NewTarget)
{
	TargetActor = NewTarget;
}

void UNobleArchimedesCameraComponent::SetInput(float YawDelta, float PitchDelta)
{
	RawYawInput = YawDelta;
	RawPitchInput = PitchDelta;
}

void UNobleArchimedesCameraComponent::EnableCollision(bool bEnable)
{
	bEnableCameraCollision = bEnable;
}

void UNobleArchimedesCameraComponent::UpdateCamera(float DeltaTime)
{
	if (!TargetActor) return;

	// Apply input rotations with sensitivity
	float Dy = RawYawInput * MouseSensitivity * 100.0f;
	float Dp = RawPitchInput * MouseSensitivity * 100.0f;

	TargetYaw += Dy;
	TargetPitch += Dp;

	// Wrap yaw
	while (TargetYaw > 180.0f) TargetYaw -= 360.0f;
	while (TargetYaw < -180.0f) TargetYaw += 360.0f;

	// Clamp pitch
	TargetPitch = FMath::Clamp(TargetPitch, PitchMin, PitchMax);

	// Smooth interpolate yaw and pitch
	CurrentYaw = FMath::FInterpTo(CurrentYaw, TargetYaw, DeltaTime, SmoothingSpeed);
	CurrentPitch = FMath::FInterpTo(CurrentPitch, TargetPitch, DeltaTime, SmoothingSpeed);

	// Smooth interpolate distance and FOV
	float TargetDist = 420.0f;
	float TargetFov = 70.0f;

	switch (CurrentMode)
	{
	case ECameraMode::Classic:
		TargetDist = ClassicDistance;
		TargetFov = ClassicFOV;
		break;
	case ECameraMode::ActionOrbit:
		TargetDist = ActionOrbitDistance;
		TargetFov = ActionOrbitFOV;
		break;
	case ECameraMode::OverTheShoulder:
		TargetDist = OverTheShoulderDistance;
		TargetFov = OverTheShoulderFOV;
		break;
	}

	CurrentDistance = FMath::FInterpTo(CurrentDistance, TargetDist, DeltaTime, FOVSmoothingSpeed);
	CurrentFOV = FMath::FInterpTo(CurrentFOV, TargetFov, DeltaTime, FOVSmoothingSpeed);

	// Calculate camera position
	FVector TargetLoc = TargetActor->GetActorLocation();
	FVector Offset = CalculateSphericalOffset(CurrentYaw, CurrentPitch, CurrentDistance);
	FVector DesiredPos = TargetLoc + Offset;

	// Add height offset
	DesiredPos.Z += 100.0f; // Camera height above target

	// Smooth position
	CurrentLocation = FMath::VInterpTo(CurrentLocation, DesiredPos, DeltaTime, PositionSmoothingSpeed);

	// Camera collision
	if (bEnableCameraCollision)
	{
		CurrentLocation = CheckCameraCollision(TargetLoc, CurrentLocation);
	}

	// Apply to camera component
	if (UCameraComponent* Cam = Cast<UCameraComponent>(GetOwner()->GetComponentByClass(UCameraComponent::StaticClass())))
	{
		Cam->SetWorldLocationAndRotation(CurrentLocation, FRotator(-CurrentPitch, CurrentYaw, 0.0f));
		Cam->SetFieldOfView(CurrentFOV);
	}
}

FVector UNobleArchimedesCameraComponent::CalculateSphericalOffset(float Yaw, float Pitch, float Distance) const
{
	float CosPitch = FMath::Cos(FMath::DegreesToRadians(Pitch));
	float SinPitch = FMath::Sin(FMath::DegreesToRadians(Pitch));
	float SinYaw = FMath::Sin(FMath::DegreesToRadians(Yaw));
	float CosYaw = FMath::Cos(FMath::DegreesToRadians(Yaw));

	return FVector(
		-Distance * CosPitch * SinYaw,
		-Distance * CosPitch * CosYaw,
		Distance * SinPitch
	);
}

FVector UNobleArchimedesCameraComponent::CheckCameraCollision(FVector TargetPos, FVector CameraPos) const
{
	FVector HitLocation = CameraPos;

	// Line trace from target to camera position
	FHitResult HitResult;
	FCollisionQueryParams QueryParams;
	QueryParams.AddIgnoredActor(TargetActor);
	QueryParams.bTraceComplex = true;

	if (GetWorld()->LineTraceSingleByChannel(HitResult, TargetPos, CameraPos, ECC_Visibility, QueryParams))
	{
		HitLocation = HitResult.ImpactPoint;
		// Pull back slightly from surface
		HitLocation += HitResult.ImpactNormal * 10.0f;
	}

	return HitLocation;
}