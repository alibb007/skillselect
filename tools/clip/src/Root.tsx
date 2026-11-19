import React from "react";
import { Composition } from "remotion";
import "./fonts";
import { Film, SECONDS } from "./Film";

const FPS = 30;
export const Root: React.FC = () => (
  <Composition id="Demo" component={Film} durationInFrames={Math.round(SECONDS * FPS)} fps={FPS} width={1920} height={1080} />
);
