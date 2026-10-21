// Fills out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"

class UAnimInstance;

/**
 * Writes blueprint-declared anim instance variables from C++.
 *
 * AB_Hector's state machine transitions on bIsMoving / bIsRunning / bIsIdle, but
 * nothing ever set them: the anim blueprint has no event graph wiring and Python
 * cannot author one, so the machine sat in Idle and the mesh held the reference
 * pose. Setting the variables from the owning character drives the same
 * transitions the event graph would have.
 */
namespace AnimVariableBridge
{
	/** Set a bool variable declared on a blueprint anim instance. No-op if absent. */
	void SetBool(UAnimInstance* AnimInstance, FName VariableName, bool Value);
}
