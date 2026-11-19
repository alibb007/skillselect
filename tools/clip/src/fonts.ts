// Fonts (all SIL Open Font License): Bricolage Grotesque, Inter, JetBrains Mono.
// Put BricolageGrotesque.ttf, Inter.ttf and JetBrainsMono.ttf in tools/clip/public/fonts before rendering.
import { continueRender, delayRender, staticFile } from "remotion";

const load = (family: string, file: string, weight: string) => {
  const handle = delayRender("font " + family);
  const face = new FontFace(family, `url(${staticFile("fonts/" + file)})`, { weight });
  face.load().then(() => { (document.fonts as any).add(face); continueRender(handle); })
    .catch((e) => { console.error(e); continueRender(handle); });
};
load("Bricolage", "BricolageGrotesque.ttf", "200 800");
load("InterV", "Inter.ttf", "100 900");
load("JBMono", "JetBrainsMono.ttf", "100 800");
