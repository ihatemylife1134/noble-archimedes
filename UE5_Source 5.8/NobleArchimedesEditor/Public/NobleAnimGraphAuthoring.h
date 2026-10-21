// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "NobleAnimGraphAuthoring.generated.h"

class UAnimBlueprint;
class UAnimSequence;
class UAnimStateNode;
class UAnimStateTransitionNode;
class UAnimationStateMachineGraph;

/**
 * Script-callable helpers for authoring Animation Blueprint state machines.
 *
 * UE 5.8 does not let Python add nodes to an AnimationStateMachineGraph: the
 * graph's Nodes/EntryNode arrays and UAnimStateNode::BoundGraph are plain
 * UPROPERTYs, which PropertyAccessUtil denies to script. This library performs
 * the same construction the editor's "Add State" / drag-transition actions do,
 * so the content pipeline can generate the Hector state machine.
 *
 * Every entry point is idempotent: running the build twice does not duplicate
 * states or transitions.
 */
UCLASS()
class NOBLEARCHIMEDESEDITOR_API UNobleAnimGraphAuthoring : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Returns the AnimBlueprint's animation graph, creating nothing. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static UAnimationStateMachineGraph* GetOrCreateStateMachine(UAnimBlueprint* AnimBlueprint,
		FName MachineName = FName("Locomotion"));

	/** Adds a state playing Sequence, or returns the existing state of that name. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static UAnimStateNode* AddState(UAnimationStateMachineGraph* StateMachine,
		FName StateName, UAnimSequence* Sequence, bool bLoop);

	/** Adds a transition between two states, reusing an existing one if present. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static UAnimStateTransitionNode* AddTransition(UAnimationStateMachineGraph* StateMachine,
		UAnimStateNode* FromState, UAnimStateNode* ToState, float CrossfadeSeconds,
		bool bAutomaticRule);

	/** Makes the state machine entry node point at FirstState. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static bool SetEntryState(UAnimationStateMachineGraph* StateMachine, UAnimStateNode* FirstState);

	/** Adds a bool member variable to the AnimBlueprint (no-op if it exists). */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static bool AddBoolVariable(UAnimBlueprint* AnimBlueprint, FName VariableName,
		bool bDefaultValue);

	/** Uses a bool variable as a transition rule (true = take the transition). */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static bool SetTransitionRuleVariable(UAnimStateTransitionNode* Transition,
		FName VariableName);

	/** Compiles the AnimBlueprint and reports whether it produced a class. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static bool CompileAnimBlueprint(UAnimBlueprint* AnimBlueprint);

	/** Lists the state names in a state machine, for verification. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static TArray<FName> GetStateNames(UAnimationStateMachineGraph* StateMachine);

	/** Counts transitions in a state machine, for verification. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static int32 GetTransitionCount(UAnimationStateMachineGraph* StateMachine);
};
