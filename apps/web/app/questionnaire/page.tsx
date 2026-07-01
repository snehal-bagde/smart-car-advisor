"use client";

import { ArrowLeft, ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { QuestionShell } from "@/components/questionnaire/QuestionShell";
import { Button } from "@/components/ui/Button";
import { ChoiceCard } from "@/components/ui/ChoiceCard";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { Slider } from "@/components/ui/Slider";
import { Stepper } from "@/components/ui/Stepper";
import { draftToRequest, requestToDraft } from "@/lib/answers-convert";
import { loadAnswers, saveAnswers } from "@/lib/answers-storage";
import { formatInrShort, formatKm } from "@/lib/format";
import {
  BODY_TYPE_OPTIONS,
  FUEL_OPTIONS,
  PRIORITY_OPTIONS,
  TRANSMISSION_OPTIONS,
  USAGE_OPTIONS,
} from "@/lib/questionnaire-options";
import type { DraftAnswers } from "@/lib/types";

const TOTAL_STEPS = 8;

const DEFAULT_ANSWERS: DraftAnswers = {
  budget: 1_000_000,
  daily_driving_distance_km: 20,
  primary_usage: null,
  family_size: 4,
  fuel_preference: null,
  transmission_preference: null,
  body_type_preference: [],
  priorities: [],
};

export default function QuestionnairePage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<DraftAnswers>(DEFAULT_ANSWERS);

  // Prefill from a previous submission (e.g. returning here after a "no matches" result)
  // in an effect, not the initial render -- sessionStorage isn't available during SSR, and
  // reading it during the lazy useState initializer would cause a hydration mismatch.
  useEffect(() => {
    const previous = loadAnswers();
    if (previous) setAnswers(requestToDraft(previous));
  }, []);

  const canContinue = step === 2 ? answers.primary_usage !== null : true;

  function goNext() {
    if (!canContinue) return;
    if (step < TOTAL_STEPS - 1) {
      setStep((current) => current + 1);
      return;
    }
    saveAnswers(draftToRequest(answers));
    router.push("/recommendations");
  }

  function goBack() {
    if (step === 0) {
      router.push("/");
      return;
    }
    setStep((current) => current - 1);
  }

  function toggleBodyType(value: DraftAnswers["body_type_preference"][number]) {
    setAnswers((prev) => ({
      ...prev,
      body_type_preference: prev.body_type_preference.includes(value)
        ? prev.body_type_preference.filter((item) => item !== value)
        : [...prev.body_type_preference, value],
    }));
  }

  function togglePriority(value: DraftAnswers["priorities"][number]) {
    setAnswers((prev) => ({
      ...prev,
      priorities: prev.priorities.includes(value)
        ? prev.priorities.filter((item) => item !== value)
        : [...prev.priorities, value],
    }));
  }

  return (
    <main className="flex flex-1 flex-col items-center justify-center px-6 py-12">
      <div className="w-full max-w-xl">
        <ProgressBar current={step + 1} total={TOTAL_STEPS} />

        <div className="mt-10">
          {step === 0 && (
            <QuestionShell
              title="What's your budget?"
              subtitle="Drag the slider to set the most you'd like to spend."
            >
              <Slider
                value={answers.budget}
                min={300_000}
                max={15_000_000}
                step={50_000}
                onChange={(budget) => setAnswers((prev) => ({ ...prev, budget }))}
                valueLabel={formatInrShort(answers.budget)}
                minLabel="₹3 L"
                maxLabel="₹1.5 Cr"
              />
            </QuestionShell>
          )}

          {step === 1 && (
            <QuestionShell
              title="How far do you drive each day?"
              subtitle="A rough daily average is fine."
            >
              <Slider
                value={answers.daily_driving_distance_km}
                min={0}
                max={150}
                step={5}
                onChange={(daily_driving_distance_km) =>
                  setAnswers((prev) => ({ ...prev, daily_driving_distance_km }))
                }
                valueLabel={formatKm(answers.daily_driving_distance_km)}
                minLabel="0 km"
                maxLabel="150+ km"
              />
            </QuestionShell>
          )}

          {step === 2 && (
            <QuestionShell title="Where do you drive most often?">
              <div className="flex flex-col gap-3">
                {USAGE_OPTIONS.map((option) => (
                  <ChoiceCard
                    key={option.value}
                    label={option.label}
                    description={option.description}
                    selected={answers.primary_usage === option.value}
                    onClick={() => setAnswers((prev) => ({ ...prev, primary_usage: option.value }))}
                  />
                ))}
              </div>
            </QuestionShell>
          )}

          {step === 3 && (
            <QuestionShell
              title="How many people usually ride with you?"
              subtitle="Include yourself."
            >
              <Stepper
                value={answers.family_size}
                min={1}
                max={9}
                onChange={(family_size) => setAnswers((prev) => ({ ...prev, family_size }))}
                unitLabel={(value) => (value === 1 ? "person" : "people")}
              />
            </QuestionShell>
          )}

          {step === 4 && (
            <QuestionShell title="Any fuel type you prefer?">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {FUEL_OPTIONS.map((option) => (
                  <ChoiceCard
                    key={option.label}
                    label={option.label}
                    icon={<option.icon className="h-4.5 w-4.5" />}
                    selected={answers.fuel_preference === option.value}
                    onClick={() =>
                      setAnswers((prev) => ({ ...prev, fuel_preference: option.value }))
                    }
                  />
                ))}
              </div>
            </QuestionShell>
          )}

          {step === 5 && (
            <QuestionShell title="Preferred transmission?">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {TRANSMISSION_OPTIONS.map((option) => (
                  <ChoiceCard
                    key={option.label}
                    label={option.label}
                    selected={answers.transmission_preference === option.value}
                    onClick={() =>
                      setAnswers((prev) => ({ ...prev, transmission_preference: option.value }))
                    }
                  />
                ))}
              </div>
            </QuestionShell>
          )}

          {step === 6 && (
            <QuestionShell
              title="Any body type in mind?"
              subtitle="Pick as many as you like, or skip if you're open to anything."
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {BODY_TYPE_OPTIONS.map((option) => (
                  <ChoiceCard
                    key={option.value}
                    label={option.label}
                    icon={<option.icon className="h-4.5 w-4.5" />}
                    selected={answers.body_type_preference.includes(option.value)}
                    onClick={() => toggleBodyType(option.value)}
                  />
                ))}
              </div>
            </QuestionShell>
          )}

          {step === 7 && (
            <QuestionShell
              title="What matters most to you?"
              subtitle="Pick anything that's important — or nothing, if you're not sure yet."
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {PRIORITY_OPTIONS.map((option) => (
                  <ChoiceCard
                    key={option.value}
                    label={option.label}
                    icon={<option.icon className="h-4.5 w-4.5" />}
                    selected={answers.priorities.includes(option.value)}
                    onClick={() => togglePriority(option.value)}
                  />
                ))}
              </div>
            </QuestionShell>
          )}
        </div>

        <div className="mt-10 flex items-center justify-between">
          <Button variant="ghost" onClick={goBack}>
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
          <Button onClick={goNext} disabled={!canContinue}>
            {step === TOTAL_STEPS - 1 ? "Get my recommendations" : "Continue"}
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </main>
  );
}
