// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NobleArchimedesTypes.h"
#include "NobleArchimedesCameraComponent.generated.h"

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class NOBLEARCHIMEDES_API UNobleArchimedesCameraComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UNobleArchimedesCameraComponent();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	//=============================================================================
	// CAMERA MODES
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Camera")
	void SetMode(ECameraMode NewMode);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Camera")
	ECameraMode GetMode() const { return CurrentMode; }

	UFUNCTION(BlueprintCallable, Category = "Camera")
	void ToggleMode();

	//=============================================================================
	// CAMERA SETTINGS
	//=============================================================================

	UFUNCTION(BlueprintCallable, Category = "Camera")
	void SetTarget(AActor* NewTarget);

	UFUNCTION(BlueprintCallable, Category = "Camera")
	void SetInput(float YawDelta, float PitchDelta);

	UFUNCTION(BlueprintCallable, Category = "Camera")
	void EnableCollision(bool bEnable);

protected:
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Camera")
	float ClassicDistance = 420.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Camera")
	float ClassicFOV = 70.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Camera")
	float ActionOrbitDistance = 360.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Camera")
	float ActionOrbitFOV = 78.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Camera")
	float OverTheShoulderDistance = 175.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Camera")
	float OverTheShoulderFOV = 65.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Camera")
	float PitchMin = -63.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Camera")
	float PitchMax = 74.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Camera")
	float SmoothingSpeed = 18.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Camera")
	float FOVSmoothingSpeed = 10.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Camera")
	float PositionSmoothingSpeed = 24.0f;

private:
	ECameraMode CurrentMode = ECameraMode::Classic;

	AActor* TargetActor = nullptr;

	float CurrentYaw = 0.0f;
	float CurrentPitch = 0.0f;
	float TargetYaw = 0.0f;
	float TargetPitch = 0.0f;

	float CurrentDistance = 420.0f;
	float TargetDistance = 420.0f;

	float CurrentFOV = 70.0f;
	float TargetFOV = 70.0f;

	FVector CurrentLocation = FVector::ZeroVector;
	FVector TargetLocation = FVector::ZeroVector;

	float MouseSensitivity = 0.0022f;
	float StickSensitivity = 2.4f;

	bool bEnableCameraCollision = true;

	float RawYawInput = 0.0f;
	float RawPitchInput = 0.0f;

	void UpdateCamera(float DeltaTime);
	FVector CalculateSphericalOffset(float Yaw, float Pitch, float Distance) const;
	FVector CheckCameraCollision(FVector TargetPos, FVector CameraPos) const;
};