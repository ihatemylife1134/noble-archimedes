// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ChapterPortal.generated.h"

class UBoxComponent;
class UStaticMeshComponent;

/**
 * A chapter exit. It stays inactive while a boss in the current level is alive,
 * then completes the current chapter and opens the next level when the player
 * walks into it.
 */
UCLASS()
class NOBLEARCHIMEDES_API AChapterPortal : public AActor
{
	GENERATED_BODY()

public:
	AChapterPortal();

	virtual void Tick(float DeltaSeconds) override;

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Chapter")
	bool CanActivate() const;

	UFUNCTION(BlueprintCallable, Category = "Chapter")
	void ActivatePortal();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chapter")
	int32 TargetChapter = 2;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chapter")
	FName TargetLevelName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chapter")
	bool bRequireBossDefeated = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chapter")
	bool bCompleteCurrentChapter = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chapter")
	float ActivationRadius = 240.0f;

protected:
	virtual void BeginPlay() override;

	UFUNCTION()
	void OnTriggerBeginOverlap(
		UPrimitiveComponent* OverlappedComponent,
		AActor* OtherActor,
		UPrimitiveComponent* OtherComp,
		int32 OtherBodyIndex,
		bool bFromSweep,
		const FHitResult& SweepResult);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UBoxComponent> Trigger;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> PortalMesh;

private:
	bool bActivating = false;
};
