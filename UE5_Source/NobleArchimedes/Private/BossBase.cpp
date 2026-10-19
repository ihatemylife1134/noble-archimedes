// Fill out your copyright notice in the Description page of Project Settings.

#include "BossBase.h"

// Sets default values
ABossBase::ABossBase()
{
	bIsBoss = true;
	BossPhase = 1;
	bHasSecondPhase = false;
	bHasThirdPhase = false;
}

void ABossBase::BeginPlay()
{
	Super::BeginPlay();

	// Bosses have higher health and detection range
	MaxHealth *= 5.0f; // Bosses are 5x tougher
	CurrentHealth = MaxHealth;
	DetectionRange *= 1.5f; // Bosses detect player from further away

	// Set up phase transition thresholds
	PhaseTransitionHealthThresholds.Empty();
	if (bHasSecondPhase)
	{
		PhaseTransitionHealthThresholds.Add(0.5f); // Transition at 50% health
	}
	if (bHasThirdPhase)
	{
		PhaseTransitionHealthThresholds.Add(0.25f); // Transition at 25% health
	}
}

void ABossBase::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (bIsDead) return;

	CheckPhaseTransition();
}

void ABossBase::TransitionToPhase(int32 NewPhase)
{
	BossPhase = NewPhase;

	// Boss phase transition effects would be handled in Blueprint
	// - Play phase transition animation
	// - Change attack patterns
	// - Update visual appearance
}

bool ABossBase::IsPhaseTransitionNeeded() const
{
	if (CurrentHealth <= 0.0f || MaxHealth <= 0.0f) return false;

	float HealthPercent = CurrentHealth / MaxHealth;

	for (float Threshold : PhaseTransitionHealthThresholds)
	{
		if (HealthPercent <= Threshold && BossPhase < MaxBossPhases)
		{
			return true;
		}
	}

	return false;
}

void ABossBase::CheckPhaseTransition()
{
	if (IsPhaseTransitionNeeded())
	{
		int32 NextPhase = BossPhase + 1;
		TransitionToPhase(NextPhase);
	}
}

void ABossBase::PlayBossIntro()
{
	// Boss intro cutscene would be triggered here
}

void ABossBase::PlayBossVictory()
{
	// Boss victory animation would be played here
}
