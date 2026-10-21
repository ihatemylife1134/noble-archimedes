// Fills out your copyright notice in the Description page of Project Settings.

#include "AnimVariableBridge.h"
#include "Animation/AnimInstance.h"
#include "UObject/UnrealType.h"

namespace
{
	// Property lookups cost a name search, so cache per anim class.
	TMap<TPair<TWeakObjectPtr<UClass>, FName>, FBoolProperty*> SBoolProperties;
}

void AnimVariableBridge::SetBool(UAnimInstance* AnimInstance, FName VariableName, bool Value)
{
	if (!AnimInstance)
	{
		return;
	}

	UClass* AnimClass = AnimInstance->GetClass();
	const TPair<TWeakObjectPtr<UClass>, FName> Key(TWeakObjectPtr<UClass>(AnimClass), VariableName);

	FBoolProperty** Cached = SBoolProperties.Find(Key);
	if (!Cached)
	{
		FBoolProperty* Found = FindFProperty<FBoolProperty>(AnimClass, VariableName);
		Cached = &SBoolProperties.Add(Key, Found);
	}

	if (FBoolProperty* Property = *Cached)
	{
		Property->SetPropertyValue_InContainer(AnimInstance, Value);
		return;
	}

	// Warn once per variable so a missing property cannot silently leave the
	// state machine stuck in Idle, which is how the T-pose went unnoticed.
	static TSet<TPair<TWeakObjectPtr<UClass>, FName>> SWarned;
	if (!SWarned.Contains(Key))
	{
		SWarned.Add(Key);
		UE_LOG(LogTemp, Warning,
			TEXT("AnimVariableBridge: %s has no bool variable '%s'; locomotion will not follow."),
			*GetNameSafe(AnimClass), *VariableName.ToString());
	}
}
