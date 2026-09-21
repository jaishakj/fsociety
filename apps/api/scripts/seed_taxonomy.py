"""Seeds the full 9-category human-reality taxonomy.

Safe to re-run: every domain/concept lookup checks for an existing
row by slug before inserting. Two topics in category 1 (Confirmation
bias, Cognitive dissonance) already exist from the earlier pilot seed
under the old ad-hoc "psychology" domain — this script does not
re-parent or duplicate them, it leaves them exactly where they are
and just links them into the new taxonomy's relation graph, so
nothing already published gets touched.
"""

from sqlalchemy import select

from app.db.session import SessionLocal
from app.modules.reality.concepts.models import (
    Concept,
    ConceptRelation,
    ConceptTag,
    ContentStatus,
    Difficulty,
    EvidenceLevel,
    RelationType,
    Tag,
)
from app.modules.reality.concepts.service import slugify
from app.modules.reality.domains.models import Domain

DOMAINS = [
    {"slug": "human-psychology", "name": "Human Psychology", "description": "How the mind actually works: biases, motivation, emotion, and group behavior."},
    {"slug": "social-behavior-and-influence", "name": "Social Behavior & Influence", "description": "How people affect each other: persuasion, trust, cooperation, and norms."},
    {"slug": "science-and-reality", "name": "Science & Reality", "description": "How we know what's true, and what the best current evidence says about the physical world."},
    {"slug": "beliefs-and-philosophy", "name": "Beliefs & Philosophy", "description": "How people make sense of meaning, ethics, and existence, presented without picking a side."},
    {"slug": "society-and-civilization", "name": "Society & Civilization", "description": "How societies organize, govern, and distribute power and resources."},
    {"slug": "neurodiversity-and-human-differences", "name": "Neurodiversity & Human Differences", "description": "Evidence-based coverage of neurological and cognitive difference, without treating it as a defect or a superpower."},
    {"slug": "relationships-and-raising-children", "name": "Relationships & Raising Children", "description": "How healthy relationships and child development actually work."},
    {"slug": "future-and-technology", "name": "Future & Technology", "description": "Where technology and civilization may be headed, and the open questions along the way."},
    {"slug": "human-sexuality-attraction-and-status", "name": "Human Sexuality, Attraction & Status", "description": "Evidence-based coverage of attraction and status, with limitations and alternative explanations stated, not treated as universal law."},
]

# CONCEPTS and RELATIONS are appended below, one category block at a time.

CAT1_HUMAN_PSYCHOLOGY = [
    {"title": "Cognitive Biases", "domain": "human-psychology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "Systematic, predictable patterns in how the mind processes information that cause judgment to depart from a purely rational standard.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Cognitive biases are not random mistakes, they are consistent, repeatable deviations from optimal reasoning that show up across cultures and contexts. Most arise from mental shortcuts (heuristics) that are fast and usually useful, but that produce predictable errors in specific situations."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Recognizing that a bias is a normal, largely automatic feature of how brains process information, not a sign of low intelligence, is the first step toward correcting for it in decisions that actually matter."},
     ], "tags": ["cognitive-bias", "reasoning"]},

    {"title": "Dunning-Kruger Effect", "domain": "human-psychology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.MIXED,
     "summary": "People with limited skill in a domain often overestimate their competence, partly because the skills needed to perform well overlap with the skills needed to judge performance accurately.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Named after a 1999 study, it describes a gap between perceived and actual ability that tends to be largest among low performers in a given skill."},
        {"type": "nuance", "title": "Evidence and limitations", "content": "Later statistical re-analyses have questioned how much of the original pattern reflects a real psychological effect versus a mathematical artifact of how self-assessment scores were correlated with test scores, so it is best treated as a useful hypothesis rather than settled law."},
     ], "tags": ["cognitive-bias", "self-perception"]},

    {"title": "Availability Heuristic", "domain": "human-psychology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "Judging how likely something is by how easily examples come to mind, rather than by its actual frequency.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "If examples of something are easy to recall, vivid, or recent, people assume it is more common than it really is."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It explains why dramatic but rare risks, like plane crashes, feel scarier than common but unremarkable ones, like heart disease, and why news coverage can badly distort public perception of risk."},
     ], "tags": ["cognitive-bias", "reasoning"]},

    {"title": "Fundamental Attribution Error", "domain": "human-psychology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "The tendency to explain other people's behavior by their character, while explaining our own behavior by our circumstances.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "If a stranger cuts you off in traffic, it is easy to assume they are reckless; if you cut someone off, it is easy to explain it as an unusual, justified exception."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "This asymmetry fuels unfair judgments and everyday conflict, since identical actions get read completely differently depending on who commits them and who is judging."},
     ], "tags": ["cognitive-bias", "social-perception"]},

    {"title": "Self-Serving Bias", "domain": "human-psychology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "The tendency to credit yourself for successes and attribute failures to outside factors.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "A student who does well credits their own ability; a student who does poorly blames an unfair test, a common and largely unconscious pattern."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It protects self-esteem in the short term, but can quietly block honest learning from mistakes if left unchecked."},
     ], "tags": ["cognitive-bias", "self-perception"]},

    {"title": "Social Comparison", "domain": "human-psychology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "People evaluate their own abilities, achievements, and worth by comparing themselves to others, especially when no objective standard exists.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "First formalized by Leon Festinger in 1954, the theory holds that in the absence of a clear yardstick, people default to comparing themselves with people around them."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It drives a lot of everyday motivation and envy, and helps explain why curated social media comparisons can be especially distorting."},
     ], "tags": ["self-perception", "social-behavior"]},

    {"title": "Learned Helplessness", "domain": "human-psychology", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "After repeated exposure to an uncontrollable negative situation, people and animals often stop trying to change their circumstances, even once escape becomes possible.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Documented in Martin Seligman's animal research in the late 1960s, the pattern occurs when repeated failure to influence an outcome teaches a general expectation that effort will not help."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It is central to understanding depression and chronic stress, and explains why encouragement alone is often not enough to undo a deeply learned pattern of giving up."},
     ], "tags": ["motivation", "mental-health"]},

    {"title": "Motivation", "domain": "human-psychology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The internal and external forces that drive people to act, commonly split into intrinsic (doing something for its own sake) and extrinsic (doing it for reward or to avoid punishment) motivation.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Self-determination theory, one of the most tested frameworks, argues motivation is strongest when three needs are met: autonomy, competence, and relatedness."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research consistently finds intrinsic motivation sustains effort and creativity better over the long run, and that heavy-handed external rewards can sometimes crowd it out."},
     ], "tags": ["motivation"]},

    {"title": "Habit Formation", "domain": "human-psychology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "How repeated behavior performed in a stable context becomes automatic, requiring progressively less conscious effort.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Habits form through a cue-routine-reward loop: a trigger in the environment leads to a behavior, which is reinforced by some payoff, strengthening the association each time."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Understanding this loop is generally more useful for changing behavior than relying on willpower alone, since it points to changing cues and environments rather than just trying harder."},
     ], "tags": ["motivation", "self-control"]},

    {"title": "Self-Control", "domain": "human-psychology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.MIXED,
     "summary": "The capacity to regulate impulses in service of longer-term goals.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Self-control lets people delay immediate gratification for a larger later reward, studied for decades as a predictor of life outcomes."},
        {"type": "nuance", "title": "Evidence and limitations", "content": "Early research, including the famous 'marshmallow test,' suggested self-control was a fixed, depletable resource, but larger replication studies have complicated that picture: a child's trust that the promised later reward will actually arrive, and their environment more broadly, seem to matter as much as willpower itself."},
     ], "tags": ["self-control", "motivation"]},

    {"title": "Emotional Regulation", "domain": "human-psychology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The strategies people use to influence which emotions they have, when they have them, and how they express them.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Strategies range from changing the situation, to shifting attention, to reframing how a situation is interpreted (cognitive reappraisal), to suppressing the outward expression of a feeling."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research consistently finds reappraisal tends to work better long-term than suppression, which can paradoxically increase stress and even impair memory of the situation."},
     ], "tags": ["emotion", "self-control"]},

    {"title": "Attachment", "domain": "human-psychology", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The early bond formed between a child and caregiver, linked by decades of research to how people approach closeness and trust in relationships throughout life.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Based on the work of John Bowlby and Mary Ainsworth, attachment theory describes patterns, commonly labeled secure, anxious, avoidant, and disorganized, that reflect how consistently a caregiver responded to a child's needs."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "These are tendencies shaped by experience, not fixed personality labels, and research shows they can shift over time through new relationships and deliberate effort."},
     ], "tags": ["attachment", "relationships"]},

    {"title": "Social Anxiety", "domain": "human-psychology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "A persistent, intense fear of being judged or embarrassed in social situations that goes well beyond ordinary shyness.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Unlike situational nervousness, social anxiety disorder involves significant, ongoing distress or avoidance that interferes with daily life."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Distinguishing everyday shyness from a diagnosable disorder matters in practice, since the latter tends to respond well to established treatments like cognitive behavioral therapy."},
     ], "tags": ["mental-health", "social-anxiety"]},

    {"title": "Charisma", "domain": "human-psychology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "A learnable set of communication behaviors, warmth, confidence, and presence, that make someone influential and likable, rather than a fixed trait people either have or lack.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Studies of charismatic communication identify specific, trainable tactics, vivid and concrete language, expressed conviction, appropriate emotional display, and confident nonverbal presence, that reliably increase perceived charisma."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Because these tactics are specific and learnable, charisma responds to deliberate practice far more than the popular 'you either have it or you don't' framing suggests."},
     ], "tags": ["charisma", "communication"]},

    {"title": "Persuasion", "domain": "human-psychology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The deliberate use of communication to change someone's beliefs or behavior, studied extensively through principles like reciprocity, social proof, and authority.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Robert Cialdini's research identified a small set of principles, reciprocity, commitment, social proof, liking, authority, and scarcity, that consistently increase compliance across contexts."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Understanding these principles is as useful for recognizing and resisting manipulation as it is for communicating persuasively and ethically."},
     ], "tags": ["persuasion", "communication"]},

    {"title": "Group Psychology", "domain": "human-psychology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "How being part of a group changes how people think, feel, and act, often in ways individuals would not predict about themselves in isolation.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Groups change individual behavior through mechanisms like conformity pressure, diffusion of responsibility, and shared identity, which can shift both reasoning and emotion."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Groups can produce both better decisions than any individual, when they draw on diverse perspectives, and worse ones, through polarization or groupthink, depending heavily on how they are structured."},
     ], "tags": ["group-psychology", "social-behavior"]},

    {"title": "Conformity", "domain": "human-psychology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "Adjusting behavior or stated opinions to match a group, even when privately disagreeing.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Demonstrated famously in Solomon Asch's 1950s line-judgment experiments, where many participants gave an answer they knew was wrong simply because the rest of the group had already given it."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Conformity pressure is strongest when the group is unanimous and the person feels observed, and it weakens dramatically the moment even one other person dissents."},
     ], "tags": ["conformity", "group-psychology"]},

    {"title": "Obedience", "domain": "human-psychology", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "Complying with instructions from an authority figure, studied most famously, and most controversially, in Stanley Milgram's experiments on willingness to administer perceived harm to another person.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Milgram's 1960s studies found a majority of ordinary participants would continue administering what they believed were increasingly painful electric shocks when instructed to by an authority figure, even while expressing distress."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "The findings are often misread as proof that people are simply cruel; the more supported interpretation is that situational authority and diffused personal responsibility can override individual moral judgment in otherwise ordinary people."},
     ], "tags": ["obedience", "group-psychology"]},

    {"title": "Bystander Effect", "domain": "human-psychology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The more people who witness an emergency, the less likely any single one is to help, because responsibility feels diffused across the group.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "First studied systematically after the widely publicized 1964 Kitty Genovese case, the effect has been replicated across many types of emergencies and group sizes."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Simply knowing the effect exists is one of the more effective countermeasures, and directing help toward one specific bystander by name breaks the diffusion far more reliably than a general call for help."},
     ], "tags": ["bystander-effect", "group-psychology"]},

    {"title": "Deindividuation", "domain": "human-psychology", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.MIXED,
     "summary": "The reduced sense of individual identity and personal accountability that can occur in crowds, anonymity, or immersive group settings.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Early theory linked deindividuation to increased antisocial or aggressive behavior once individual identity feels submerged in a crowd."},
        {"type": "nuance", "title": "Evidence and limitations", "content": "More recent research suggests it is less a simple loss of identity and more a shift toward whatever norms are most salient in that specific group, which can just as easily produce prosocial, cooperative behavior as antisocial behavior."},
     ], "tags": ["group-psychology", "identity"]},
]
CONCEPTS_ALL = list(CAT1_HUMAN_PSYCHOLOGY)

CAT2_SOCIAL_INFLUENCE = [
    {"title": "Ben Franklin Effect", "domain": "social-behavior-and-influence", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "Doing someone a favor tends to make you like them more, not the other way around, an effect first noted by Benjamin Franklin.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Franklin described winning over a rival by asking to borrow a rare book from him, a small favor that reportedly turned a cold relationship warm."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It is consistent with cognitive dissonance: the mind resolves the tension of doing something kind for someone you do not especially like by quietly revising the liking upward to match the action."},
     ], "tags": ["persuasion", "social-behavior"]},

    {"title": "Reciprocity", "domain": "social-behavior-and-influence", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "People feel obligated to return favors, gifts, or concessions, one of the most consistent and universal drivers of cooperation and compliance.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Found across essentially every human culture studied, the reciprocity norm creates a felt obligation even when the original favor was small or unrequested."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It underlies gift-giving customs, diplomacy, and everyday sales tactics like free samples, and it is one of the most reliably exploited persuasion principles."},
     ], "tags": ["persuasion", "cooperation"]},

    {"title": "Mere Exposure Effect", "domain": "social-behavior-and-influence", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "Repeated exposure to something, a song, a face, a brand, tends to increase liking for it, even without conscious awareness of the exposure.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Demonstrated across hundreds of studies since the late 1960s, familiarity itself, independent of quality, reliably nudges preference upward."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It explains why familiar options often feel safer or more appealing by default, and why advertising leans so heavily on repetition."},
     ], "tags": ["persuasion", "social-behavior"]},

    {"title": "Social Proof", "domain": "social-behavior-and-influence", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "People look to others' behavior to decide what is correct, especially in ambiguous or unfamiliar situations.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "When uncertain how to act, people default to what appears to be the majority or expert behavior around them."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It is one of the most reliably exploited persuasion principles, from 'best seller' labels to canned laughter on television."},
     ], "tags": ["persuasion", "conformity"]},

    {"title": "Authority Bias", "domain": "social-behavior-and-influence", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "Giving disproportionate weight to the opinions and instructions of a perceived authority figure, sometimes regardless of the actual merit of what is being said.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Authority cues, titles, uniforms, credentials, reliably shift judgment and compliance, even when the authority figure has no real relevant expertise."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Awareness of the bias is a practical safeguard against deferring to confident-sounding authority in place of actually checking the underlying reasoning."},
     ], "tags": ["persuasion", "obedience"]},

    {"title": "Halo Effect", "domain": "social-behavior-and-influence", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "A positive impression in one area, often physical attractiveness, spills over into unrelated judgments, like assuming someone is also more competent or trustworthy.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "First named by psychologist Edward Thorndike in 1920, it has since been shown to influence hiring decisions, academic grading, and even courtroom outcomes."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Because it operates largely below conscious awareness, structured, criteria-based evaluation is one of the few reliable ways to reduce its effect."},
     ], "tags": ["cognitive-bias", "social-perception"]},

    {"title": "Impression Management", "domain": "social-behavior-and-influence", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The deliberate, and often automatic, effort people make to control how others perceive them.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Sociologist Erving Goffman compared social life to a stage, where people present different 'faces' depending on the audience and setting."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Recognizing it helps distinguish reasonable, context-appropriate self-presentation from more effortful performance, in other people and in yourself."},
     ], "tags": ["social-behavior", "identity"]},

    {"title": "Reputation", "domain": "social-behavior-and-influence", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The shared, social record of a person's past behavior that others use to predict how they will act in the future.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Reputation accumulates through both direct experience and secondhand accounts (gossip), and it travels faster than any individual can personally verify."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Reputation systems are a major reason cooperation stays stable in groups larger than one person can personally track, since bad behavior tends to get remembered and shared."},
     ], "tags": ["trust", "social-behavior"]},

    {"title": "Status", "domain": "social-behavior-and-influence", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "A person's relative standing or respect within a group, distinct from raw power or wealth though often correlated with both.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Status hierarchies show up in essentially all human groups, and in many social animal species, typically tracked through subtle cues like deference, attention, and speaking order."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Status-seeking is a major, often underacknowledged driver of everyday behavior, from career choices to how people signal taste and competence."},
     ], "tags": ["status", "social-behavior"]},

    {"title": "Trust", "domain": "social-behavior-and-influence", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The willingness to be vulnerable to another person's actions, based on the expectation that they will behave predictably and in good faith.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Trust is foundational to everything from close relationships to national economies and legal systems."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research consistently finds trust is built incrementally through consistent, verified behavior over time, not through declarations, and that it is far easier to destroy than to rebuild."},
     ], "tags": ["trust", "relationships"]},

    {"title": "Cooperation", "domain": "social-behavior-and-influence", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "Individuals working together toward a shared benefit, often at some individual cost.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Cooperation ranges from small, informal exchanges to large-scale coordination across strangers who will never meet again."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Explaining how cooperation evolved and persists despite the constant temptation to free-ride is one of the central open questions in evolutionary biology and economics."},
     ], "tags": ["cooperation", "game-theory"]},

    {"title": "Game Theory", "domain": "social-behavior-and-influence", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The mathematical study of strategic decision-making between parties whose outcomes depend on each other's choices.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Developed substantially by John von Neumann and later John Nash, game theory formalizes situations from business negotiation to nuclear deterrence."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "One of its most important findings is that choices which are individually rational for each party can still produce an outcome that is worse for everyone involved."},
     ], "tags": ["game-theory", "decision-making"]},

    {"title": "Prisoner's Dilemma", "domain": "social-behavior-and-influence", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "A classic game-theory scenario where two parties would both benefit from cooperating, but each has an individual incentive to betray the other, often leaving both worse off.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Named for a scenario where two suspects are separately offered a lighter sentence for betraying the other, it is the most widely used model for studying cooperation versus self-interest."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "In repeated versions of the game, simple reciprocity-based strategies, cooperate first, then mirror the other party's last move, tend to outperform purely selfish ones over time."},
     ], "tags": ["game-theory", "cooperation"]},

    {"title": "Altruism", "domain": "social-behavior-and-influence", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.MIXED,
     "summary": "Behavior that benefits another at a cost to oneself, with genuine scientific debate over whether truly cost-free, selfless altruism exists.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Altruism ranges from small daily kindnesses to large personal sacrifices, and appears in many social species, not only humans."},
        {"type": "nuance", "title": "Evidence and limitations", "content": "Evolutionary theories like kin selection and reciprocal altruism explain much of it in terms of indirect genetic or social payoff, but this remains actively debated rather than fully settled, especially for cases involving strangers with no realistic chance of reciprocation."},
     ], "tags": ["altruism", "cooperation"]},

    {"title": "Kin Selection", "domain": "social-behavior-and-influence", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The evolutionary tendency to favor behaviors that help genetic relatives survive and reproduce, even at a cost to the individual.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Formalized by W. D. Hamilton's rule, which predicts that helping behavior scales with how closely related the individuals are."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It explains a wide range of animal and human behavior, from parental sacrifice to nepotism, without requiring any conscious calculation on the part of the individual."},
     ], "tags": ["evolutionary-psychology", "altruism"]},

    {"title": "Cultural Evolution", "domain": "social-behavior-and-influence", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "The idea that ideas, behaviors, and social practices change over time through processes analogous to biological evolution: variation, selection, and transmission.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Practices and beliefs spread when they are successfully copied and passed on, and change when copying is imperfect or when some variants are favored over others."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It helps explain how norms and technologies spread and shift across generations independent of any genetic change, and why some ideas are far 'stickier' than others."},
     ], "tags": ["culture", "social-norms"]},

    {"title": "Social Norms", "domain": "social-behavior-and-influence", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The largely unwritten rules that govern acceptable behavior within a group, enforced through informal rewards and punishments like approval or exclusion.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Norms differ from formal laws in that they are enforced socially rather than institutionally, through reactions like praise, gossip, or shunning."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Norms are often more powerful than formal rules in shaping everyday behavior, and research shows they can shift surprisingly quickly once enough people visibly start acting differently."},
     ], "tags": ["social-norms", "conformity"]},

    {"title": "Propaganda", "domain": "social-behavior-and-influence", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "Communication deliberately designed to shape attitudes or behavior in a particular direction, typically by appealing to emotion over evidence.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Common techniques include loaded language, selective framing, repetition, and manufactured urgency, all of which work by short-circuiting careful evaluation."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Recognizing these techniques is a practical defense regardless of which side of a political or commercial debate is using them."},
     ], "tags": ["propaganda", "persuasion"]},

    {"title": "Misinformation", "domain": "social-behavior-and-influence", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "False or inaccurate information spread regardless of intent to deceive, distinct from disinformation, which is deliberately false.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Misinformation spreads through ordinary sharing behavior, often faster than corrections, partly because false or surprising claims tend to feel more novel and shareable."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research finds corrections often fail to fully undo the influence of an initial false claim, which is why prevention, checking sources before sharing, tends to outperform after-the-fact fact-checking alone."},
     ], "tags": ["misinformation", "media-literacy"]},
]
CONCEPTS_ALL += CAT2_SOCIAL_INFLUENCE

CAT3_SCIENCE_REALITY = [
    {"title": "Scientific Method", "domain": "science-and-reality", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "A systematic process for building and testing knowledge: observe, form a testable hypothesis, gather evidence, and revise the hypothesis based on what the evidence shows.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "The core loop, observation, hypothesis, prediction, test, revision, is designed specifically to catch and correct human error and bias over time, rather than relying on any single person's judgment."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Its power comes from being self-correcting: no finding is treated as final, and claims are expected to be checked by others through replication before being trusted."},
     ], "tags": ["scientific-method", "epistemology"]},

    {"title": "Bayesian Reasoning", "domain": "science-and-reality", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "Updating the strength of a belief incrementally as new evidence arrives, rather than treating beliefs as simply true or false.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Named after mathematician Thomas Bayes, it treats belief as a probability that shifts up or down based on how well new evidence fits, weighted by how strong that evidence is."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It is a more accurate model of good reasoning than all-or-nothing certainty, and it explains why the same new evidence should move a confident belief less than an uncertain one."},
     ], "tags": ["reasoning", "probability"]},

    {"title": "Correlation vs Causation", "domain": "science-and-reality", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "Two things moving together (correlation) does not by itself prove that one causes the other.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Apparent correlations can arise from one thing causing another, from a hidden third factor causing both, from pure coincidence, or from the causation actually running in the opposite direction."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Establishing real causation generally requires controlled experiments or careful statistical methods designed to rule out these alternative explanations, not just noticing that two trends move together."},
     ], "tags": ["statistical-thinking", "reasoning"]},

    {"title": "Falsifiability", "domain": "science-and-reality", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "A genuinely scientific claim must be capable, at least in principle, of being proven wrong by some possible observation.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Philosopher Karl Popper proposed this as the key line between science and non-science: a claim that could never be contradicted by any evidence is not making a testable scientific claim, whatever else it might be."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It is a useful, though not perfect or universally accepted, tool for evaluating whether a claim is genuinely being tested against reality or simply reframed to survive any possible outcome."},
     ], "tags": ["epistemology", "scientific-method"]},

    {"title": "Statistical Thinking", "domain": "science-and-reality", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "Interpreting numbers and data in a way that accounts for sample size, variability, and the ever-present possibility of chance producing a misleading pattern.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Core habits include checking sample size before trusting a result, distinguishing a meaningful effect from statistical noise, and being skeptical of small samples or cherry-picked comparisons."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Most everyday misuses of statistics, in news, marketing, and politics, exploit a lack of statistical thinking rather than outright lying with fabricated numbers."},
     ], "tags": ["statistical-thinking", "probability"]},

    {"title": "Probability", "domain": "science-and-reality", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The mathematical framework for reasoning about uncertainty and chance.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Probability quantifies how likely an event is, from impossible (0) to certain (1), and underlies everything from weather forecasts to medical test interpretation."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Human intuition about probability is notoriously unreliable, people routinely misjudge rare-event risk and misread conditional probabilities like test accuracy, which is why formal training in it improves real-world decisions."},
     ], "tags": ["probability", "statistical-thinking"]},

    {"title": "Evolution", "domain": "science-and-reality", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The process by which populations of organisms change over generations through variation, heredity, and differential survival and reproduction.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "First laid out systematically by Charles Darwin in 1859, evolutionary theory is supported by converging evidence from fossils, comparative anatomy, and, since the 20th century, genetics."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It is one of the most thoroughly evidenced theories in all of science, and it underlies modern medicine, agriculture, and conservation biology."},
     ], "tags": ["evolution", "biology"]},

    {"title": "Natural Selection", "domain": "science-and-reality", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The mechanism by which traits that improve survival and reproduction become more common in a population over time.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "It requires three ingredients: variation between individuals, heritability of that variation, and a difference in survival or reproductive success linked to it."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It is the primary, though not the only, driver of evolution, and directly observable examples, from antibiotic-resistant bacteria to moth coloration, have been documented within human lifetimes."},
     ], "tags": ["evolution", "biology"]},

    {"title": "Genetics", "domain": "science-and-reality", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The study of how traits are encoded in DNA and passed from parents to offspring.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Genes are segments of DNA that carry instructions for building and regulating an organism, inherited in patterns first described by Gregor Mendel and later explained at the molecular level."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Most human traits are shaped by many genes interacting with environment, not single 'genes for' a trait, a nuance that is frequently lost in popular reporting on genetics."},
     ], "tags": ["genetics", "biology"]},

    {"title": "Neuroscience", "domain": "science-and-reality", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The study of the nervous system, especially the brain, and how its physical structure and activity produce thought, emotion, and behavior.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Modern neuroscience draws on biology, chemistry, and increasingly computation to map how billions of interconnected neurons give rise to mental life."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It is a genuinely fast-moving field, so specific claims (especially simplified pop-science ones like 'left brain versus right brain') should be treated with more caution than the field's more settled, foundational findings."},
     ], "tags": ["neuroscience", "biology"]},

    {"title": "Human Origins", "domain": "science-and-reality", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The evolutionary history of Homo sapiens, traced through fossil, archaeological, and genetic evidence back to a shared ancestry with other great apes.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Genetic and fossil evidence converge on modern humans having evolved in Africa, with the species spreading globally over roughly the last 70,000 to 100,000 years."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Genetic evidence also shows all living humans are far more alike than different, with more genetic variation typically found within any given population than between populations."},
     ], "tags": ["evolution", "anthropology"]},

    {"title": "Astronomy", "domain": "science-and-reality", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The scientific study of celestial objects, from planets and stars to galaxies, and the physical processes that govern them.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Modern astronomy combines direct observation across the electromagnetic spectrum with physics to understand objects ranging from nearby planets to galaxies billions of light-years away."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It provides essential context for humanity's place in the universe, and its practical applications range from satellite navigation to asteroid-impact monitoring."},
     ], "tags": ["astronomy", "physics"]},

    {"title": "Cosmology", "domain": "science-and-reality", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The study of the origin, large-scale structure, and evolution of the universe as a whole.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "The Big Bang model, which describes the universe expanding from an extremely hot, dense state roughly 13.8 billion years ago, is supported by multiple independent lines of evidence, including the cosmic microwave background and the observed abundance of light elements."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "While the broad framework is well established, questions about the very earliest moments of the universe, and about dark matter and dark energy, remain active, genuinely open areas of research."},
     ], "tags": ["cosmology", "physics"]},

    {"title": "Entropy", "domain": "science-and-reality", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "A measure of disorder or the number of ways a system's parts can be arranged; the second law of thermodynamics states that total entropy in a closed system tends to increase over time.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "In practice, this is why processes like heat spreading out or ice melting happen spontaneously in one direction but not the reverse."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It is one of the most consistently confirmed principles in physics, and it underlies why energy conversion is never perfectly efficient in any real machine."},
     ], "tags": ["physics", "entropy"]},

    {"title": "Climate Science", "domain": "science-and-reality", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The study of Earth's climate system and how it is changing, drawing on physics, chemistry, and long-term observational records.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Multiple independent lines of evidence, ice cores, temperature records, satellite data, atmospheric chemistry, converge on the finding that global temperatures have risen significantly since the industrial era, driven substantially by human greenhouse gas emissions."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "This core finding reflects strong scientific consensus, though the precise pace, regional effects, and best policy responses remain areas of legitimate ongoing research and debate."},
     ], "tags": ["climate-science", "ecology"]},

    {"title": "Biodiversity", "domain": "science-and-reality", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The variety of life at every level, genes, species, and ecosystems, within a given area.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "High biodiversity generally makes ecosystems more resilient to disturbance, since a wider range of species can fill similar roles if one is lost."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Current extinction rates are estimated by researchers to be substantially higher than the long-term natural background rate, driven mainly by habitat loss, making biodiversity monitoring a practical, not just academic, concern."},
     ], "tags": ["biodiversity", "ecology"]},

    {"title": "Ecology", "domain": "science-and-reality", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The study of how organisms interact with each other and with their physical environment.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Ecology examines relationships at every scale, from individual predator-prey dynamics up to how entire ecosystems cycle energy and nutrients."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It provides the evidence base for understanding how human activity, from farming to urbanization, ripples through interconnected natural systems, often in ways that are not obvious in advance."},
     ], "tags": ["ecology", "biodiversity"]},
]
CONCEPTS_ALL += CAT3_SCIENCE_REALITY

CAT4_BELIEFS_PHILOSOPHY = [
    {"title": "Atheism", "domain": "beliefs-and-philosophy", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "The position of not believing in the existence of any god or gods.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Atheism is generally defined by an absence of belief in deities. Some atheists hold this as a simple lack of belief, while others actively assert that no god exists, a stronger claim; both are commonly grouped under the term."},
        {"type": "context", "title": "How it fits with related views", "content": "It is one of several stances people take on questions about ultimate reality, alongside agnosticism and various forms of religious belief. This entry describes the position rather than arguing for or against it."},
     ], "tags": ["belief-systems", "philosophy"]},

    {"title": "Agnosticism", "domain": "beliefs-and-philosophy", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "The position that the existence of god(s) is unknown or, in some formulations, unknowable, distinct from both atheism and theism.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Coined by biologist Thomas Huxley in 1869, agnosticism is often framed as a matter of certainty rather than belief itself: many people describe themselves as agnostic about certainty while still leaning toward belief or disbelief in practice."},
        {"type": "context", "title": "How it fits with related views", "content": "It is frequently placed on a spectrum alongside atheism and theism rather than treated as a wholly separate third category."},
     ], "tags": ["belief-systems", "philosophy"]},

    {"title": "Religion", "domain": "beliefs-and-philosophy", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "An organized system of beliefs, practices, and community centered on the sacred, the transcendent, or ultimate questions of meaning.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Religions vary enormously in structure, from highly centralized institutions to decentralized traditions, but commonly combine shared beliefs, rituals, ethical teaching, and community."},
        {"type": "context", "title": "Why it's studied", "content": "Independent of any particular tradition's truth claims, religion is studied across psychology, sociology, and anthropology for its role in meaning-making, identity, community, and behavior."},
     ], "tags": ["religion", "belief-systems"]},

    {"title": "Secular Humanism", "domain": "beliefs-and-philosophy", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "An ethical and philosophical stance that grounds meaning and morality in human reason and shared human values, without reliance on religious belief.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Secular humanism emphasizes ethics, critical thinking, and human welfare as sufficient foundations for a meaningful life and a moral framework."},
        {"type": "context", "title": "How it fits with related views", "content": "It is one of several frameworks, alongside religious and other secular traditions, that people use to ground meaning and morality."},
     ], "tags": ["belief-systems", "ethics"]},

    {"title": "Existentialism", "domain": "beliefs-and-philosophy", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "A philosophical tradition holding that individuals must create their own meaning and values in a universe that does not supply them ready-made.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Associated with thinkers including Jean-Paul Sartre, Simone de Beauvoir, and Søren Kierkegaard, existentialism emphasizes individual freedom, responsibility, and authenticity."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It remains influential in modern psychotherapy (existential therapy) as well as in philosophy, independent of whether one accepts its underlying metaphysical premises."},
     ], "tags": ["philosophy", "meaning"]},

    {"title": "Absurdism", "domain": "beliefs-and-philosophy", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "The philosophical position, most associated with Albert Camus, that humans naturally seek meaning in a universe that offers none, and that this tension itself must be honestly confronted.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Camus described this mismatch between the human need for meaning and the universe's silence on the question as 'the absurd.'"},
        {"type": "why-it-matters", "title": "Why it matters", "content": "He argued the appropriate response is neither despair nor blind faith, but a kind of defiant engagement with life anyway, famously summarized in his line that 'one must imagine Sisyphus happy.'"},
     ], "tags": ["philosophy", "meaning"]},

    {"title": "Stoicism", "domain": "beliefs-and-philosophy", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "An ancient philosophy, and a widely used modern practical framework, centered on focusing effort only on what is within one's control and accepting what is not.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Originating in ancient Greece and Rome with figures like Epictetus, Seneca, and Marcus Aurelius, Stoicism teaches that emotional suffering often comes from judgments about events rather than the events themselves."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Many of its core techniques, especially the 'dichotomy of control,' overlap substantially with the principles of modern cognitive behavioral therapy."},
     ], "tags": ["philosophy", "self-control"]},

    {"title": "Utilitarianism", "domain": "beliefs-and-philosophy", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "An ethical framework holding that the right action is the one that produces the greatest overall wellbeing for the greatest number of people.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Associated with Jeremy Bentham and John Stuart Mill, utilitarianism judges actions by their consequences rather than by rules or intentions."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It is a major, influential framework in ethics and policy, though it faces well-known challenges over how to weigh individual rights against aggregate benefit."},
     ], "tags": ["ethics", "philosophy"]},

    {"title": "Deontology", "domain": "beliefs-and-philosophy", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "An ethical framework holding that some actions are inherently right or wrong based on rules or duties, regardless of their consequences.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Most associated with Immanuel Kant, deontology insists certain moral rules, such as not using a person merely as a means to an end, should hold regardless of outcome."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It directly contrasts with utilitarianism, which would potentially justify the same rule-breaking if it produced a better overall outcome."},
     ], "tags": ["ethics", "philosophy"]},

    {"title": "Virtue Ethics", "domain": "beliefs-and-philosophy", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "An ethical framework focused less on rules or outcomes and more on cultivating good character traits, like honesty and courage, from which good actions naturally follow.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Rooted in Aristotle's writing, virtue ethics asks 'what would a person of good character do here' rather than 'what rule applies' or 'what outcome is best.'"},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It offers a third major approach alongside utilitarianism and deontology, and has seen a significant revival in modern moral philosophy."},
     ], "tags": ["ethics", "philosophy"]},

    {"title": "Moral Psychology", "domain": "beliefs-and-philosophy", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "The empirical study of how people actually form and apply moral judgments, distinct from philosophical ethics' study of which moral judgments are correct.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Researchers such as Jonathan Haidt have studied how much of everyday moral judgment appears to be driven by fast, intuitive reactions, with conscious reasoning often arriving afterward to justify a gut response rather than to produce it."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "This is an active, evolving area of empirical research; its findings inform, but do not settle, the separate philosophical question of what is actually right."},
     ], "tags": ["moral-psychology", "ethics"]},

    {"title": "Free Will", "domain": "beliefs-and-philosophy", "difficulty": Difficulty.ADVANCED, "evidence_level": EvidenceLevel.MIXED,
     "summary": "The long-standing, unresolved philosophical question of whether people genuinely choose their actions or whether every choice is ultimately determined by prior causes.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Positions range from hard determinism (no free will exists), to libertarian free will (genuine, uncaused choice is possible), to compatibilism (free will and determinism can coexist, depending on how 'freedom' is defined)."},
        {"type": "nuance", "title": "Evidence and limitations", "content": "Neuroscience findings, such as Benjamin Libet's experiments on brain activity preceding conscious decisions, are frequently cited in this debate, but their interpretation and relevance remain genuinely contested among both scientists and philosophers."},
     ], "tags": ["free-will", "philosophy"]},

    {"title": "Consciousness", "domain": "beliefs-and-philosophy", "difficulty": Difficulty.ADVANCED, "evidence_level": EvidenceLevel.SPECULATIVE,
     "summary": "Subjective, first-person experience, and one of the least understood phenomena in science, sometimes called 'the hard problem.'",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Neuroscience has mapped many neural correlates of consciousness, patterns of brain activity that accompany awareness, but this differs from explaining why or how physical brain activity gives rise to subjective experience at all."},
        {"type": "nuance", "title": "Evidence and limitations", "content": "This remains a genuinely open question across neuroscience and philosophy of mind, without a settled, broadly agreed answer."},
     ], "tags": ["consciousness", "neuroscience"]},

    {"title": "Skepticism", "domain": "beliefs-and-philosophy", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "A disposition or method of withholding belief until sufficient evidence or justification is provided.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "As a practical habit, skepticism means asking what evidence supports a claim before accepting it, distinct from full philosophical skepticism, which questions whether any certain knowledge is possible at all."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "As an everyday practice, it is one of the most useful defenses against misinformation and manipulation."},
     ], "tags": ["skepticism", "epistemology"]},

    {"title": "Epistemology", "domain": "beliefs-and-philosophy", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "The branch of philosophy concerned with the nature of knowledge: what counts as knowing something, and how that belief can be justified.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Classic epistemology asks what separates genuine knowledge from a merely true guess, typically framed around justification, truth, and belief."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "These questions underlie nearly every other topic in this taxonomy, since they set the standard for what counts as good evidence in the first place."},
     ], "tags": ["epistemology", "philosophy"]},

    {"title": "Meaning of Life", "domain": "beliefs-and-philosophy", "difficulty": Difficulty.ADVANCED, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "The broad philosophical and personal question of what, if anything, gives human life purpose or significance.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Answers span religious frameworks, secular philosophical frameworks like existentialism or humanism, and individually constructed sources of meaning such as relationships, achievement, or creativity."},
        {"type": "context", "title": "How this is presented", "content": "This entry maps the major approaches people take to the question, rather than asserting that any one of them is the demonstrably correct answer."},
     ], "tags": ["meaning", "philosophy"]},
]
CONCEPTS_ALL += CAT4_BELIEFS_PHILOSOPHY

CAT5_SOCIETY_CIVILIZATION = [
    {"title": "Capitalism", "domain": "society-and-civilization", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.MIXED,
     "summary": "An economic system based on private ownership of the means of production, with resources allocated primarily through markets and price signals.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Under capitalism, individuals and firms own capital (businesses, land, equipment) and compete to produce goods and services, with prices set largely by supply and demand."},
        {"type": "nuance", "title": "Evidence and debate", "content": "Economists broadly agree markets are effective at coordinating information and incentivizing innovation, but there is genuine, ongoing debate over how much regulation, redistribution, and public provision should accompany a market economy, a debate this entry describes rather than resolves."},
     ], "tags": ["economics", "society"]},

    {"title": "Socialism", "domain": "society-and-civilization", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.MIXED,
     "summary": "A family of economic and political systems and theories centered on collective or democratic public ownership and control of the means of production, in contrast to private ownership.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "In practice it ranges widely, from centrally planned state-run economies to market socialism to mixed economies with strong public services and worker ownership."},
        {"type": "nuance", "title": "Evidence and debate", "content": "Like capitalism, its real-world track record is debated across very different historical implementations, and conflating distinct systems under one label often obscures more than it reveals."},
     ], "tags": ["economics", "society"]},

    {"title": "Economics", "domain": "society-and-civilization", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The social science studying how individuals, businesses, and societies allocate scarce resources.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "The field splits broadly into microeconomics, the study of individual and firm decisions, and macroeconomics, the study of economy-wide patterns like inflation, unemployment, and growth."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Modern economics increasingly tests its theoretical models against empirical data and real-world experiments, though genuine disagreement remains among economists on many major policy questions."},
     ], "tags": ["economics"]},

    {"title": "Inequality", "domain": "society-and-civilization", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The uneven distribution of income, wealth, or opportunity across individuals or groups within a society.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Commonly measured using tools like the Gini coefficient, which summarizes how evenly or unevenly income or wealth is spread across a population."},
        {"type": "nuance", "title": "Evidence and debate", "content": "That inequality exists and can be measured is well established; how much of it is problematic, and what, if anything, should be done about it, are separate, actively debated economic and political questions this entry does not settle."},
     ], "tags": ["economics", "inequality"]},

    {"title": "Wealth", "domain": "society-and-civilization", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "The total value of assets a person or group owns, distinct from income, which is what they earn over a given period.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Wealth includes savings, property, investments, and other assets minus debts, a stock measured at a point in time, unlike income, which is a flow measured over a period."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Wealth and income can move quite differently, someone can have high income and low wealth, or the reverse, which matters for understanding real economic security."},
     ], "tags": ["economics", "wealth"]},

    {"title": "Poverty", "domain": "society-and-civilization", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "A lack of the financial resources needed to meet basic material needs, measured in both absolute terms (a fixed threshold) and relative terms (compared to the norms of a given society).",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Absolute poverty measures use a fixed income or consumption threshold, while relative poverty measures compare a household's resources to the typical resources in its own society."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "The choice between absolute and relative measures significantly changes both the reported scale of poverty and the policy conclusions drawn from it."},
     ], "tags": ["economics", "poverty"]},

    {"title": "Labor", "domain": "society-and-civilization", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "Human work performed in exchange for wages or in the production of goods and services.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Labor economics studies how wages, working conditions, and bargaining power, including through unions and labor law, are shaped by supply, demand, and institutions."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "How labor markets should be structured and regulated remains one of the more actively contested areas of economic policy."},
     ], "tags": ["economics", "labor"]},

    {"title": "Education", "domain": "society-and-civilization", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "The structured process of acquiring knowledge, skills, and values, both formally through schooling and informally through everyday experience.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Formal education systems vary widely across countries in structure, funding, and pedagogy."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research consistently links educational attainment with a wide range of life outcomes, though the precise causal mechanisms, skills learned, credentialing, or other factors, remain actively studied."},
     ], "tags": ["education"]},

    {"title": "Democracy", "domain": "society-and-civilization", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "A system of government in which political power derives from the people, typically through voting and representative institutions.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Democracy takes many forms, direct, representative, and constitutional among them, with different countries balancing majority rule against protections for individual rights in different ways."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Political scientists study how democratic institutions affect outcomes like stability, corruption, and economic growth, though no single model of democracy is universally agreed to be optimal."},
     ], "tags": ["democracy", "governance"]},

    {"title": "Human Rights", "domain": "society-and-civilization", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "The idea that certain basic entitlements and freedoms belong to every person simply by virtue of being human, regardless of law, culture, or government.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Formalized internationally in the 1948 Universal Declaration of Human Rights, the framework covers civil, political, economic, social, and cultural rights."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "While the general framework has wide international endorsement, the relative priority and interpretation of specific rights remains a subject of genuine cross-cultural and political debate."},
     ], "tags": ["human-rights", "governance"]},

    {"title": "Colonialism", "domain": "society-and-civilization", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The practice of one country or group establishing political and economic control over another territory and its people, typically for resource extraction and strategic advantage.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Historically widespread from roughly the 15th through 20th centuries, colonialism involved direct governance of a territory by an external power."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Its documented historical effects, including large-scale economic extraction, disrupted governance structures, and lasting demographic and cultural impact, are studied extensively across history and economics."},
     ], "tags": ["history", "colonialism"]},

    {"title": "Imperialism", "domain": "society-and-civilization", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The policy or practice of extending a state's power and influence over other territories or peoples, through direct control or indirect economic and political dominance.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Closely related to colonialism but broader, imperialism includes forms of dominance that stop short of formal territorial control, such as economic or military influence."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "It remains a live analytical lens used to study both historical empires and contemporary international power dynamics."},
     ], "tags": ["history", "imperialism"]},

    {"title": "War", "domain": "society-and-civilization", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "Organized, sustained armed conflict between states, groups, or factions.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "War has taken enormously varied forms across history, but is generally distinguished from other violence by its organized, sustained, and political nature."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Political scientists and historians study its causes, including resource competition, security dilemmas, and ideology, to better understand and, where possible, prevent it."},
     ], "tags": ["war", "conflict"]},

    {"title": "Peacebuilding", "domain": "society-and-civilization", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "Deliberate efforts to prevent, manage, or resolve violent conflict, and to build durable conditions for peace afterward.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Peacebuilding includes diplomacy, mediation, post-conflict reconstruction, and reconciliation processes between former combatants."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research on past conflicts identifies practices, such as inclusive power-sharing and addressing root economic grievances, that are associated with more durable peace after conflict ends."},
     ], "tags": ["peacebuilding", "conflict"]},

    {"title": "Feminism", "domain": "society-and-civilization", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "A range of social, political, and intellectual movements and perspectives centered on achieving equality between genders.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Feminism is not a single unified position; it spans multiple distinct traditions, including liberal, radical, and intersectional feminism, with differing emphases and, at times, disagreements among themselves."},
        {"type": "context", "title": "How this is presented", "content": "This entry describes feminism as a family of perspectives studied in sociology and political science, not as a single settled position."},
     ], "tags": ["feminism", "society"]},

    {"title": "Gender Roles", "domain": "society-and-civilization", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.MIXED,
     "summary": "The behaviors, expectations, and responsibilities a society associates with being a man or a woman.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Gender roles vary substantially across cultures and historical periods, which researchers take as evidence that at least part of their content is socially shaped rather than fixed."},
        {"type": "nuance", "title": "Evidence and debate", "content": "The relative contribution of biology versus culture to specific observed gender differences in behavior is an active, genuinely contested area of research, not a settled question with one agreed answer."},
     ], "tags": ["gender", "society"]},

    {"title": "Patriarchy", "domain": "society-and-civilization", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.MIXED,
     "summary": "A term used in social science to describe social systems in which men hold disproportionate power and authority in political, economic, or family structures.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "The term is widely used in sociology and history to describe documented historical and ongoing patterns of male-dominated authority in many, though not all, societies."},
        {"type": "nuance", "title": "Evidence and debate", "content": "The extent, causes, and the most accurate way to characterize these patterns in any specific society or period remain subjects of real academic and political debate, which this entry does not settle."},
     ], "tags": ["gender", "society"]},

    {"title": "Social Justice", "domain": "society-and-civilization", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "The concept of fair and equitable distribution of rights, opportunities, and resources within a society.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Different traditions define fairness differently, ranging from equal treatment under existing rules, to equal opportunity, to equal outcomes, and these differing definitions lead to different policy conclusions."},
        {"type": "context", "title": "How this is presented", "content": "This entry treats social justice as a family of related concepts and ongoing debates, not a single agreed-upon standard."},
     ], "tags": ["social-justice", "society"]},

    {"title": "Media Literacy", "domain": "society-and-civilization", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The practical skill of critically evaluating media sources, including checking for bias, verifying claims, and understanding how content is produced and incentivized.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Core practices include checking a claim's original source, distinguishing news from opinion, and understanding how a platform's incentives shape what gets shown."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research links stronger media literacy skills to reduced susceptibility to misinformation, making it one of the more directly actionable topics in this category."},
     ], "tags": ["media-literacy", "misinformation"]},
]
CONCEPTS_ALL += CAT5_SOCIETY_CIVILIZATION

CAT6_NEURODIVERSITY = [
    {"title": "Autism", "domain": "neurodiversity-and-human-differences", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "A neurodevelopmental difference characterized by differences in social communication and interaction, alongside restricted or repetitive behaviors and interests.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Autism is diagnosed based on behavioral criteria and exists as a spectrum, meaning presentation and support needs vary widely between individuals."},
        {"type": "nuance", "title": "Evidence and framing", "content": "Current research increasingly frames autism as a difference in how the brain processes information rather than a single deficit. At the same time, many autistic people have genuine support needs and co-occurring challenges, such as sensory sensitivity or communication barriers, that benefit from evidence-based support. Neither a purely 'superpower' framing nor a purely 'defect' framing reflects the evidence well."},
     ], "tags": ["autism", "neurodivergence"]},

    {"title": "ADHD", "domain": "neurodiversity-and-human-differences", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "A neurodevelopmental condition involving persistent differences in attention regulation, impulse control, and activity level that meaningfully impact daily functioning.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "ADHD reflects measurable differences in brain networks related to attention and executive function, not simply a matter of willpower or discipline."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Evidence-based strategies, environmental supports, and for many people medication, have been shown in research to meaningfully help manage its challenges."},
     ], "tags": ["adhd", "neurodivergence"]},

    {"title": "Dyslexia", "domain": "neurodiversity-and-human-differences", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "A specific learning difference primarily affecting the accuracy and fluency of reading and spelling, unrelated to overall intelligence.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Research links dyslexia to differences in how the brain processes phonological, sound-based, information, rather than to a lack of effort or general ability."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Structured, evidence-based reading instruction methods have been repeatedly shown to meaningfully help dyslexic readers build fluency."},
     ], "tags": ["dyslexia", "neurodivergence"]},

    {"title": "Neurodivergence", "domain": "neurodiversity-and-human-differences", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "An umbrella term describing brains that function in ways that diverge from what is considered typical, including autism, ADHD, dyslexia, and other conditions.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "The term grew out of the neurodiversity framing, which holds that neurological differences are part of natural human variation rather than being only deficits to correct."},
        {"type": "context", "title": "How this is presented", "content": "This framing coexists with the reality that many neurodivergent people also have genuine, specific support needs. The two are not contradictory, and evidence-based support remains valuable regardless of framing."},
     ], "tags": ["neurodivergence"]},

    {"title": "Sensory Processing", "domain": "neurodiversity-and-human-differences", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "How the nervous system receives, organizes, and responds to sensory information from the body and environment, which can differ substantially between individuals.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Differences can involve both heightened and reduced sensitivity to input such as sound, light, texture, or touch."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "These differences are common among neurodivergent people, and understanding them helps explain behaviors, like avoiding certain environments, that might otherwise be misread as simple preference or defiance."},
     ], "tags": ["sensory-processing", "neurodivergence"]},

    {"title": "Executive Function", "domain": "neurodiversity-and-human-differences", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The set of mental skills, including planning, working memory, flexible thinking, and impulse control, that let people manage tasks and regulate behavior toward a goal.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "These skills are coordinated largely by the brain's prefrontal cortex and develop gradually from childhood into early adulthood."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Executive function differences are central to ADHD and several other conditions, and practical supports, like external structure and checklists, can meaningfully offset specific weaknesses."},
     ], "tags": ["executive-function", "neurodivergence"]},

    {"title": "Communication Differences", "domain": "neurodiversity-and-human-differences", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "Variations in how people express themselves and interpret communication from others, including differences in eye contact, tone interpretation, directness, and nonverbal cues.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Many communication differences, common among autistic and other neurodivergent people, reflect a genuinely different communication style rather than a deficit in the underlying ability to communicate."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research on the 'double empathy problem' suggests mismatches often arise between different communication styles on both sides, rather than from one side simply being wrong."},
     ], "tags": ["communication", "neurodivergence"]},

    {"title": "Disability Models", "domain": "neurodiversity-and-human-differences", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "Different frameworks for understanding disability, primarily the medical model, disability as an individual condition to treat, and the social model, disability arising from a mismatch between a person and an inaccessible environment.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "The medical model focuses on diagnosis and treatment; the social model focuses on removing environmental and social barriers."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Most modern disability scholarship and policy draws on both models to some degree, since real individual needs and real environmental barriers both matter."},
     ], "tags": ["disability", "accessibility"]},

    {"title": "Accessibility", "domain": "neurodiversity-and-human-differences", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The design of environments, products, and information so they can be used by people with a wide range of abilities.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Accessible design includes things like captions, ramps, screen-reader-friendly layouts, and clear plain-language writing."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Accessible design frequently ends up benefiting people well beyond its original target group, a pattern often referred to as the curb-cut effect."},
     ], "tags": ["accessibility", "disability"]},

    {"title": "Inclusion", "domain": "neurodiversity-and-human-differences", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "The practice of ensuring people with differences, including disability and neurodivergence, are genuinely welcomed and able to participate fully, not merely present.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Inclusion is distinct from mere integration or presence; it requires environments and attitudes actively adapted to support real participation."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research in education and workplace settings consistently links genuine inclusion, not just physical presence, to better outcomes for the people it is meant to support."},
     ], "tags": ["inclusion", "disability"]},

    {"title": "Masking", "domain": "neurodiversity-and-human-differences", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "The effort some neurodivergent people make to consciously suppress or hide natural traits in order to appear more neurotypical in a given social setting.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Masking can include suppressing repetitive movements, forcing eye contact, or rehearsing scripted responses in advance of social situations."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research links sustained masking to increased stress and exhaustion, and to delayed diagnosis, historically especially common in women and girls, making it a genuine cost worth understanding rather than a minor personal quirk."},
     ], "tags": ["masking", "neurodivergence"]},

    {"title": "Identity and Self-Acceptance", "domain": "neurodiversity-and-human-differences", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "The process of understanding, integrating, and accepting one's own neurodivergent or otherwise different traits as part of a coherent sense of self.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "This process often includes learning accurate information about a difference, connecting with others who share it, and separating the trait itself from any negative meaning attached to it by others."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research on disability and neurodivergent identity finds that self-acceptance, combined with appropriate support, is associated with better wellbeing than either denying the difference or feeling constant pressure to 'overcome' it."},
     ], "tags": ["identity", "self-acceptance"]},
]
CONCEPTS_ALL += CAT6_NEURODIVERSITY

CAT7_RELATIONSHIPS_CHILDREN = [
    {"title": "Parenting Styles", "domain": "relationships-and-raising-children", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "Broad patterns of parenting behavior, commonly categorized by psychologist Diana Baumrind into authoritative, authoritarian, permissive, and later neglectful or uninvolved styles.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "The categories are distinguished mainly along two dimensions: warmth and responsiveness, and structure and expectations."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research consistently associates the authoritative style, high warmth paired with high structure, with generally better child outcomes across many studied populations, though cultural context also shapes which style is typical and effective."},
     ], "tags": ["parenting", "child-development"]},

    {"title": "Child Development", "domain": "relationships-and-raising-children", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The physical, cognitive, emotional, and social changes children undergo from birth through adolescence.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Development follows broadly predictable stages and sequences, though the pace varies meaningfully between individual children."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Understanding typical developmental milestones helps distinguish normal individual variation from signs that may warrant further support."},
     ], "tags": ["child-development"]},

    {"title": "Emotional Safety", "domain": "relationships-and-raising-children", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "A relationship or environment in which a person can express feelings and needs without fear of ridicule, punishment, or rejection.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "It is built through consistent, predictable, and non-punitive responses to a person's expressed feelings over time."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research on child development and adult relationships consistently links emotional safety to healthier attachment, more open communication, and better long-term mental health outcomes."},
     ], "tags": ["emotional-safety", "relationships"]},

    {"title": "Communication in Relationships", "domain": "relationships-and-raising-children", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The exchange of information, needs, and feelings between people, one of the most heavily researched predictors of relationship quality.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Long-term relationship research, notably John Gottman's, has identified specific communication patterns that reliably predict relationship outcomes over years."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Patterns like contempt and stonewalling are strongly linked to relationship breakdown, while active listening and genuine repair attempts after conflict are linked to relationship durability."},
     ], "tags": ["communication", "relationships"]},

    {"title": "Boundaries", "domain": "relationships-and-raising-children", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "The limits a person sets on what behavior they will accept from others, in order to protect their own wellbeing.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Healthy boundaries are typically described as clear and respectfully communicated, distinct from both rigid emotional walls and an absence of limits altogether."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research associates clearly communicated boundaries with lower relationship conflict and lower burnout in caregiving and close relationships."},
     ], "tags": ["boundaries", "relationships"]},

    {"title": "Conflict Resolution", "domain": "relationships-and-raising-children", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "The process and skills used to address disagreement in a way that resolves the underlying issue without unnecessary damage to the relationship.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Effective conflict resolution typically involves naming the actual underlying need, listening without immediately rebutting, and working toward a solution both people can accept."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research finds relationship health depends less on avoiding conflict altogether, which is normal and can even be healthy, and more on how disagreement is handled, especially whether repair attempts are made and received."},
     ], "tags": ["conflict-resolution", "relationships"]},

    {"title": "Empathy", "domain": "relationships-and-raising-children", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The capacity to understand, and to some extent share, another person's feelings and perspective.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Researchers commonly distinguish cognitive empathy, understanding what someone feels, from affective empathy, feeling it alongside them."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Empathy is measurably trainable through deliberate perspective-taking practice, it is not simply a fixed trait some people have and others lack."},
     ], "tags": ["empathy", "relationships"]},

    {"title": "Consent", "domain": "relationships-and-raising-children", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "Clear, voluntary, and ongoing agreement to participate in an activity, understood as something that can be withdrawn at any time.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Genuine consent requires a real choice, free of coercion or pressure, and clear communication rather than assumption."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Clinical and educational guidance consistently emphasizes that silence or a lack of resistance is not the same thing as consent."},
     ], "tags": ["consent", "relationships"]},

    {"title": "Healthy Relationships", "domain": "relationships-and-raising-children", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "Relationships generally characterized by mutual respect, trust, honest communication, and support for each person's individual wellbeing and autonomy.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Researchers commonly identify markers such as trust, fairness, and the ability to disagree without fear as central features."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "These markers function as protective factors in research, associated with better mental health, in clear contrast to relationships marked by control, fear, or persistent disrespect."},
     ], "tags": ["healthy-relationships"]},

    {"title": "Social Development", "domain": "relationships-and-raising-children", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "How children and adolescents develop the skills to interact with others, form relationships, and understand social norms over time.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Social development draws on both innate temperament and learned experience gained through interaction with caregivers, peers, and community."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Early social skill development is linked in longitudinal research to later relationship quality and academic outcomes."},
     ], "tags": ["social-development", "child-development"]},

    {"title": "Gender Socialization", "domain": "relationships-and-raising-children", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "The process by which children learn gender-related expectations, behaviors, and roles from family, peers, media, and culture.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Research finds this process begins very early and operates through many subtle channels, including the toys, praise, and language directed at a child."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Because it shapes how gender roles are learned and reinforced generation to generation, the topic connects closely to broader research on gender roles more generally."},
     ], "tags": ["gender", "child-development"]},

    {"title": "Intergenerational Trauma", "domain": "relationships-and-raising-children", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.MIXED,
     "summary": "The idea that the effects of trauma experienced by one generation can influence the wellbeing, behavior, or stress responses of subsequent generations, through psychological, social, and possibly biological pathways.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Research spans documented psychological and behavioral transmission, such as parenting patterns and family communication about trauma, as well as more actively studied biological pathways like epigenetics."},
        {"type": "nuance", "title": "Evidence and limitations", "content": "The psychological and social transmission pathways are more strongly evidenced than some proposed biological mechanisms, which remain an active and genuinely contested area of research, so specific mechanism claims should be treated with appropriate caution."},
     ], "tags": ["trauma", "family"]},
]
CONCEPTS_ALL += CAT7_RELATIONSHIPS_CHILDREN

CAT8_FUTURE_TECHNOLOGY = [
    {"title": "Artificial Intelligence", "domain": "future-and-technology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The field of building computer systems that perform tasks normally requiring human intelligence, like understanding language, recognizing patterns, or making decisions.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Modern AI capability has advanced rapidly since the 2010s, driven substantially by deep learning methods trained on large datasets."},
        {"type": "nuance", "title": "Evidence and limitations", "content": "Current systems remain narrow in important ways; general-purpose common sense and reliable factual accuracy across all domains remain open engineering and research challenges, not solved problems."},
     ], "tags": ["artificial-intelligence", "technology"]},

    {"title": "Automation", "domain": "future-and-technology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The use of technology to perform tasks that previously required human labor, with a long history stretching back well before computers.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Automation has ranged from mechanical looms to assembly lines to, more recently, software and AI systems performing cognitive tasks."},
        {"type": "nuance", "title": "Evidence and debate", "content": "Historically, automation has eliminated specific jobs while also creating new ones; economists actively debate whether the current AI-driven wave will follow that same pattern or differ meaningfully in scale or speed."},
     ], "tags": ["automation", "technology"]},

    {"title": "AI Alignment", "domain": "future-and-technology", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.MIXED,
     "summary": "The research problem of ensuring advanced AI systems reliably pursue the goals and values their designers and users actually intend, rather than unintended proxies or side effects.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "As AI systems become more capable and are given more autonomy, ensuring their behavior stays reliably aligned with intended goals becomes both more important and more technically difficult."},
        {"type": "nuance", "title": "Evidence and limitations", "content": "This is an active, unsolved area of research. Researchers genuinely disagree on how difficult the problem will prove for more capable future systems, and this entry does not assert a settled answer either way."},
     ], "tags": ["ai-alignment", "artificial-intelligence"]},

    {"title": "AI Ethics", "domain": "future-and-technology", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "The study of the moral questions raised by building and deploying AI systems, including bias, accountability, transparency, and the appropriate scope of automated decision-making.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "The field covers documented issues, like bias inherited from training data, as well as open normative questions, like how much high-stakes decision-making, such as hiring or lending, should be delegated to automated systems at all."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "These are live policy and design questions being actively worked out across industry, government, and academia, not settled by any single consensus answer yet."},
     ], "tags": ["ai-ethics", "artificial-intelligence"]},

    {"title": "Technological Unemployment", "domain": "future-and-technology", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.MIXED,
     "summary": "The concern that automation and AI could eliminate jobs faster than new ones are created, leading to structural unemployment rather than the temporary disruption seen in past waves of automation.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Past waves of automation historically ended up creating more jobs than they destroyed, though often with painful transition periods for displaced workers."},
        {"type": "nuance", "title": "Evidence and debate", "content": "Economists are genuinely divided on whether that historical pattern will hold this time; some argue AI's breadth, potentially affecting cognitive as well as physical labor, makes past comparisons less reliable, a debate this entry does not resolve."},
     ], "tags": ["automation", "economics"]},

    {"title": "Surveillance", "domain": "future-and-technology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "The monitoring of behavior, communication, or activity by governments, companies, or other parties.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Modern digital surveillance capability, from data collection to facial recognition, has expanded dramatically compared to earlier eras."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Researchers and civil society groups actively study the tradeoffs between surveillance's stated security or commercial benefits and its costs to privacy and civil liberties."},
     ], "tags": ["surveillance", "privacy"]},

    {"title": "Privacy", "domain": "future-and-technology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "The ability of an individual to control what personal information about them is known or accessible to others.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Privacy covers control over personal data, communications, physical space, and decisions, and is protected to varying degrees by different legal systems."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "What counts as a reasonable expectation of privacy varies across cultures and has shifted substantially with digital technology, an active area of legal and ethical debate rather than a fixed standard."},
     ], "tags": ["privacy", "technology"]},

    {"title": "Digital Addiction", "domain": "future-and-technology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.MIXED,
     "summary": "Compulsive or difficult-to-control use of digital devices or platforms, sometimes to the point of interfering with daily functioning or wellbeing.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Common features include loss of control over use, continued use despite negative consequences, and use as a primary coping mechanism for difficult emotions."},
        {"type": "nuance", "title": "Evidence and limitations", "content": "Whether 'addiction' is the most clinically accurate term for problematic technology use, versus a related but distinct pattern, remains debated among researchers, though the underlying behavioral patterns are well documented."},
     ], "tags": ["digital-wellbeing", "technology"]},

    {"title": "Solarpunk", "domain": "future-and-technology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.NOT_APPLICABLE,
     "summary": "A cultural and design movement imagining futures that combine advanced, sustainable technology with ecological restoration and community, as an alternative to both dystopian and purely techno-utilitarian visions of the future.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Solarpunk is expressed mainly through fiction, visual art, and speculative design, imagining cities and technologies built around renewable energy and reconnection with nature."},
        {"type": "context", "title": "How this is presented", "content": "This entry treats it as a speculative cultural and design movement, not as a set of empirically testable claims."},
     ], "tags": ["solarpunk", "sustainability"]},

    {"title": "Sustainable Cities", "domain": "future-and-technology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "Urban design and planning approaches aimed at reducing environmental impact while maintaining or improving quality of life for residents.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Common strategies include dense, walkable development, efficient public transit, and integrating green space into urban planning."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research links these design choices to meaningfully reduced per-capita emissions compared to sprawling, car-dependent development."},
     ], "tags": ["sustainability", "urban-planning"]},

    {"title": "Renewable Energy", "domain": "future-and-technology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "Energy generated from naturally replenishing sources, like sunlight, wind, and water, as opposed to finite fossil fuels.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "The cost of solar and wind generation has fallen dramatically over the past two decades, and their share of global electricity generation continues to grow."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Questions of energy storage, grid integration, and the pace of transition away from fossil fuels remain active engineering and policy challenges, not fully solved problems."},
     ], "tags": ["renewable-energy", "sustainability"]},

    {"title": "Climate Adaptation", "domain": "future-and-technology", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "Adjusting infrastructure, practices, and systems to reduce harm from the effects of climate change that are already occurring or considered locked in.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Distinct from mitigation, which focuses on reducing future emissions, adaptation focuses on managing consequences that are already underway or unavoidable."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "Research identifies specific strategies, such as updated building codes and early-warning systems, that measurably reduce harm from climate-related events."},
     ], "tags": ["climate-adaptation", "sustainability"]},

    {"title": "Long-termism", "domain": "future-and-technology", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.MIXED,
     "summary": "The philosophical view that positively influencing the long-term future should be a key moral priority, given the vast number of people who could potentially exist in the future.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Long-termist arguments often focus on reducing risks that could permanently curtail humanity's future, such as global catastrophic risks."},
        {"type": "nuance", "title": "Evidence and debate", "content": "It has drawn both serious philosophical engagement and significant criticism, including concerns that focusing heavily on speculative future outcomes could distract from addressing well-documented present-day harms, a genuinely contested debate this entry does not resolve."},
     ], "tags": ["long-termism", "philosophy"]},

    {"title": "Space Exploration", "domain": "future-and-technology", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "Human and robotic efforts to study and travel beyond Earth's atmosphere.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Space exploration spans robotic probes, satellites, and crewed missions, and has produced substantial scientific and technological advances since the mid-20th century."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "While its scientific and technological benefits are well documented, the case for large-scale human settlement of other worlds in the near term remains a subject of genuine debate among scientists and policymakers."},
     ], "tags": ["space-exploration", "technology"]},

    {"title": "Civilization Resilience", "domain": "future-and-technology", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.MIXED,
     "summary": "The study of what makes societies able to withstand and recover from major shocks, whether natural disasters, pandemics, or systemic failures.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Researchers draw on historical case studies of societal collapse and recovery to identify recurring factors, such as resource diversity and institutional flexibility, associated with resilience."},
        {"type": "nuance", "title": "Evidence and limitations", "content": "Explaining resilience after the fact is considerably easier than predicting it in advance, and this remains a genuinely harder, more contested problem."},
     ], "tags": ["resilience", "society"]},
]
CONCEPTS_ALL += CAT8_FUTURE_TECHNOLOGY

CAT9_SEXUALITY_ATTRACTION_STATUS = [
    {"title": "Attraction", "domain": "human-sexuality-attraction-and-status", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.MIXED,
     "summary": "The psychological and physiological pull toward another person, studied through a mix of evolutionary, psychological, and cultural lenses that each explain part, but not all, of the picture.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Research finds some patterns that recur across many cultures, such as a general preference for facial symmetry, alongside substantial variation in what is considered attractive across time periods and cultures."},
        {"type": "nuance", "title": "Evidence and alternative explanations", "content": "Evolutionary explanations for attraction offer one useful lens but are actively debated. Cultural learning, individual experience, and social context all measurably shape attraction as well, and reducing attraction to any single explanation oversimplifies genuinely mixed evidence."},
     ], "tags": ["attraction", "evolutionary-psychology"]},

    {"title": "Mate Preferences", "domain": "human-sexuality-attraction-and-status", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.MIXED,
     "summary": "The traits people report valuing when selecting a partner, studied extensively but with real debate over how much reported preferences predict actual partner choice.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Large cross-cultural surveys, notably David Buss's studies across dozens of countries, have found some broadly recurring patterns in self-reported preferences, alongside meaningful cultural variation."},
        {"type": "nuance", "title": "Evidence and limitations", "content": "A significant, well-documented body of research finds people's stated preferences on surveys often diverge from who they actually pursue and choose in real interactions, so self-report data should be interpreted cautiously, not as a direct window into real-world mate choice."},
     ], "tags": ["mate-preferences", "evolutionary-psychology"]},

    {"title": "Sexual Selection", "domain": "human-sexuality-attraction-and-status", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "An evolutionary process, distinct from natural selection, in which traits increase in a population because they improve mating success specifically, not survival more broadly.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Proposed by Charles Darwin, sexual selection explains traits like elaborate peacock feathers, which offer no survival advantage and can even carry a survival cost, but which improve mating success."},
        {"type": "nuance", "title": "Evidence and limitations", "content": "The mechanism itself is well documented across many species. Applying it to explain specific human psychological or behavioral traits is a separate, more contested extension that researchers actively debate case by case."},
     ], "tags": ["sexual-selection", "evolutionary-psychology"]},

    {"title": "Hypergamy", "domain": "human-sexuality-attraction-and-status", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.SPECULATIVE,
     "summary": "A term describing a pattern where a person partners with someone of higher social or economic status, sometimes proposed in evolutionary psychology as a general mating strategy, though this specific framing is genuinely contested and not settled science.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "The underlying observation, that status and resources are commonly reported as valued partner traits in some surveys, has partial empirical support."},
        {"type": "nuance", "title": "Evidence, limitations, and alternative explanations", "content": "Treating hypergamy as a fixed, universal law explaining most or all relationships is not supported by the evidence. Actual partner choice is shaped by a wide mix of individual values, economic structure, cultural context, and personal history, and cross-cultural research finds real variation in how much status differentials factor into pairing. This entry presents it as one contested hypothesis among several, not an established rule."},
     ], "tags": ["hypergamy", "evolutionary-psychology"]},

    {"title": "Relationship Formation", "domain": "human-sexuality-attraction-and-status", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.SUPPORTED,
     "summary": "The psychological and social processes by which people meet, become attracted to, and commit to romantic partners.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Research identifies contributing factors including physical proximity, similarity, reciprocal liking, and timing in a person's life."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "No single factor reliably predicts relationship formation on its own; researchers generally describe it as the product of many interacting factors rather than one dominant cause."},
     ], "tags": ["relationship-formation", "attraction"]},

    {"title": "Gender Differences", "domain": "human-sexuality-attraction-and-status", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.MIXED,
     "summary": "Measured average differences in behavior, cognition, or preference between men and women, an area where the size and even the direction of specific differences is far more debated than popular discussion often suggests.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Meta-analyses generally find many psychological gender differences are small in effect size with substantial overlap between the distributions for men and women, alongside a smaller number of differences with more consistently replicated, larger effect sizes."},
        {"type": "nuance", "title": "Evidence and debate", "content": "The relative contribution of biological and cultural or environmental factors to any specific observed difference is genuinely and actively contested in the research literature; this entry does not assert one explanation over the other for any specific trait."},
     ], "tags": ["gender", "evolutionary-psychology"]},

    {"title": "Cultural Variation in Attraction and Mating", "domain": "human-sexuality-attraction-and-status", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "What is considered attractive, and how relationships and marriage are structured, varies substantially across human cultures and historical periods.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Anthropological and cross-cultural research documents wide variation in beauty standards, courtship practices, and family and marriage structures across societies."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "This variation is itself important evidence used to evaluate how much of human attraction and mating behavior is fixed by biology versus shaped by culture and circumstance, a genuinely open and actively studied question."},
     ], "tags": ["culture", "attraction"]},

    {"title": "Evolutionary Psychology", "domain": "human-sexuality-attraction-and-status", "difficulty": Difficulty.INTERMEDIATE, "evidence_level": EvidenceLevel.MIXED,
     "summary": "A field that studies psychological traits as potential products of evolution by natural or sexual selection, alongside significant methodological debate over how to test such explanations rigorously.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "Proponents argue certain recurring psychological patterns make sense as adaptations to ancestral environments."},
        {"type": "nuance", "title": "Evidence and limitations", "content": "Critics, including many psychologists and biologists, raise real methodological concerns, including that many evolutionary explanations are difficult to rigorously test or falsify after the fact. Specific evolutionary psychology claims about human behavior should be evaluated individually and cautiously, not accepted as a package."},
     ], "tags": ["evolutionary-psychology"]},

    {"title": "Sexual Dimorphism", "domain": "human-sexuality-attraction-and-status", "difficulty": Difficulty.BEGINNER, "evidence_level": EvidenceLevel.WELL_ESTABLISHED,
     "summary": "Measurable physical differences between males and females of a species, present to varying degrees across the animal kingdom, including humans.",
     "sections": [
        {"type": "definition", "title": "What it is", "content": "In humans this includes average differences in height, muscle mass, and other physical traits, alongside substantial individual variation and overlap between the sexes."},
        {"type": "why-it-matters", "title": "Why it matters", "content": "The existence of average physical dimorphism is well documented; it is separate from, and does not by itself determine, questions about average psychological or behavioral differences, which are a distinct and more contested area of research."},
     ], "tags": ["sexual-dimorphism", "biology"]},
]
CONCEPTS_ALL += CAT9_SEXUALITY_ATTRACTION_STATUS

# (from_title, to_title, relation_type) — resolved to slugs at seed time.
# Covers natural clusters within and across categories, plus links the
# pre-existing pilot concepts (Confirmation Bias, Cognitive Dissonance)
# into the new taxonomy without duplicating them.
RELATIONS_BY_TITLE = [
    # Cognitive biases cluster
    ("Cognitive Biases", "Confirmation Bias", RelationType.RELATED),
    ("Cognitive Biases", "Dunning-Kruger Effect", RelationType.RELATED),
    ("Cognitive Biases", "Availability Heuristic", RelationType.RELATED),
    ("Cognitive Biases", "Fundamental Attribution Error", RelationType.RELATED),
    ("Cognitive Biases", "Self-Serving Bias", RelationType.RELATED),
    ("Cognitive Biases", "Halo Effect", RelationType.RELATED),
    ("Confirmation Bias", "Cognitive Dissonance", RelationType.RELATED),
    ("Dunning-Kruger Effect", "Self-Serving Bias", RelationType.RELATED),
    ("Fundamental Attribution Error", "Self-Serving Bias", RelationType.RELATED),

    # Motivation / self-control cluster
    ("Motivation", "Habit Formation", RelationType.RELATED),
    ("Motivation", "Self-Control", RelationType.RELATED),
    ("Self-Control", "Emotional Regulation", RelationType.RELATED),
    ("Habit Formation", "Executive Function", RelationType.RELATED),
    ("Learned Helplessness", "Motivation", RelationType.RELATED),

    # Group psychology cluster
    ("Group Psychology", "Conformity", RelationType.RELATED),
    ("Group Psychology", "Obedience", RelationType.RELATED),
    ("Group Psychology", "Bystander Effect", RelationType.RELATED),
    ("Group Psychology", "Deindividuation", RelationType.RELATED),
    ("Conformity", "Social Proof", RelationType.RELATED),
    ("Obedience", "Authority Bias", RelationType.RELATED),
    ("Bystander Effect", "Deindividuation", RelationType.RELATED),

    # Social influence / persuasion cluster
    ("Persuasion", "Reciprocity", RelationType.RELATED),
    ("Persuasion", "Social Proof", RelationType.RELATED),
    ("Persuasion", "Authority Bias", RelationType.RELATED),
    ("Persuasion", "Charisma", RelationType.RELATED),
    ("Persuasion", "Propaganda", RelationType.RELATED),
    ("Ben Franklin Effect", "Cognitive Dissonance", RelationType.RELATED),
    ("Ben Franklin Effect", "Reciprocity", RelationType.RELATED),
    ("Mere Exposure Effect", "Social Proof", RelationType.RELATED),
    ("Halo Effect", "Impression Management", RelationType.RELATED),
    ("Reputation", "Trust", RelationType.RELATED),
    ("Reputation", "Status", RelationType.RELATED),
    ("Status", "Hypergamy", RelationType.RELATED),

    # Cooperation / game theory cluster
    ("Cooperation", "Game Theory", RelationType.RELATED),
    ("Game Theory", "Prisoner's Dilemma", RelationType.RELATED),
    ("Prisoner's Dilemma", "Trust", RelationType.RELATED),
    ("Altruism", "Kin Selection", RelationType.RELATED),
    ("Cooperation", "Altruism", RelationType.RELATED),
    ("Social Norms", "Cultural Evolution", RelationType.RELATED),
    ("Propaganda", "Misinformation", RelationType.RELATED),
    ("Misinformation", "Media Literacy", RelationType.RELATED),

    # Science and reasoning cluster
    ("Scientific Method", "Falsifiability", RelationType.RELATED),
    ("Scientific Method", "Bayesian Reasoning", RelationType.RELATED),
    ("Scientific Method", "Correlation vs Causation", RelationType.RELATED),
    ("Bayesian Reasoning", "Probability", RelationType.RELATED),
    ("Statistical Thinking", "Probability", RelationType.RELATED),
    ("Statistical Thinking", "Correlation vs Causation", RelationType.RELATED),
    ("Skepticism", "Scientific Method", RelationType.RELATED),
    ("Skepticism", "Epistemology", RelationType.RELATED),
    ("Epistemology", "Falsifiability", RelationType.RELATED),

    # Evolution / biology cluster
    ("Evolution", "Natural Selection", RelationType.RELATED),
    ("Natural Selection", "Genetics", RelationType.RELATED),
    ("Evolution", "Human Origins", RelationType.RELATED),
    ("Evolution", "Sexual Selection", RelationType.RELATED),
    ("Biodiversity", "Ecology", RelationType.RELATED),
    ("Climate Science", "Ecology", RelationType.RELATED),
    ("Astronomy", "Cosmology", RelationType.RELATED),
    ("Cosmology", "Entropy", RelationType.RELATED),
    ("Neuroscience", "Consciousness", RelationType.RELATED),
    ("Neuroscience", "Free Will", RelationType.RELATED),

    # Philosophy / ethics cluster
    ("Utilitarianism", "Deontology", RelationType.RELATED),
    ("Deontology", "Virtue Ethics", RelationType.RELATED),
    ("Virtue Ethics", "Utilitarianism", RelationType.RELATED),
    ("Moral Psychology", "Utilitarianism", RelationType.RELATED),
    ("Free Will", "Consciousness", RelationType.RELATED),
    ("Existentialism", "Absurdism", RelationType.RELATED),
    ("Existentialism", "Meaning of Life", RelationType.RELATED),
    ("Absurdism", "Meaning of Life", RelationType.RELATED),
    ("Stoicism", "Meaning of Life", RelationType.RELATED),
    ("Stoicism", "Emotional Regulation", RelationType.RELATED),
    ("Atheism", "Agnosticism", RelationType.RELATED),
    ("Atheism", "Religion", RelationType.RELATED),
    ("Agnosticism", "Religion", RelationType.RELATED),
    ("Secular Humanism", "Religion", RelationType.RELATED),
    ("Secular Humanism", "Meaning of Life", RelationType.RELATED),
    ("Skepticism", "Atheism", RelationType.RELATED),

    # Society / economics / politics cluster
    ("Capitalism", "Socialism", RelationType.RELATED),
    ("Capitalism", "Economics", RelationType.RELATED),
    ("Socialism", "Economics", RelationType.RELATED),
    ("Economics", "Inequality", RelationType.RELATED),
    ("Inequality", "Wealth", RelationType.RELATED),
    ("Inequality", "Poverty", RelationType.RELATED),
    ("Poverty", "Labor", RelationType.RELATED),
    ("Labor", "Economics", RelationType.RELATED),
    ("Democracy", "Human Rights", RelationType.RELATED),
    ("Human Rights", "Social Justice", RelationType.RELATED),
    ("Colonialism", "Imperialism", RelationType.RELATED),
    ("Imperialism", "War", RelationType.RELATED),
    ("War", "Peacebuilding", RelationType.RELATED),
    ("Feminism", "Gender Roles", RelationType.RELATED),
    ("Feminism", "Patriarchy", RelationType.RELATED),
    ("Gender Roles", "Patriarchy", RelationType.RELATED),
    ("Gender Roles", "Social Justice", RelationType.RELATED),
    ("Media Literacy", "Misinformation", RelationType.RELATED),

    # Neurodiversity cluster
    ("Neurodivergence", "Autism", RelationType.RELATED),
    ("Neurodivergence", "ADHD", RelationType.RELATED),
    ("Neurodivergence", "Dyslexia", RelationType.RELATED),
    ("Autism", "Sensory Processing", RelationType.RELATED),
    ("Autism", "Communication Differences", RelationType.RELATED),
    ("Autism", "Masking", RelationType.RELATED),
    ("ADHD", "Executive Function", RelationType.RELATED),
    ("Dyslexia", "Executive Function", RelationType.RELATED),
    ("Masking", "Identity and Self-Acceptance", RelationType.RELATED),
    ("Disability Models", "Accessibility", RelationType.RELATED),
    ("Accessibility", "Inclusion", RelationType.RELATED),
    ("Inclusion", "Identity and Self-Acceptance", RelationType.RELATED),

    # Relationships / children cluster
    ("Parenting Styles", "Child Development", RelationType.RELATED),
    ("Child Development", "Social Development", RelationType.RELATED),
    ("Emotional Safety", "Attachment", RelationType.RELATED),
    ("Communication in Relationships", "Conflict Resolution", RelationType.RELATED),
    ("Conflict Resolution", "Boundaries", RelationType.RELATED),
    ("Boundaries", "Consent", RelationType.RELATED),
    ("Healthy Relationships", "Trust", RelationType.RELATED),
    ("Healthy Relationships", "Communication in Relationships", RelationType.RELATED),
    ("Empathy", "Emotional Regulation", RelationType.RELATED),
    ("Gender Socialization", "Gender Roles", RelationType.RELATED),
    ("Intergenerational Trauma", "Attachment", RelationType.RELATED),

    # Future / technology cluster
    ("Artificial Intelligence", "Automation", RelationType.RELATED),
    ("Artificial Intelligence", "AI Alignment", RelationType.RELATED),
    ("AI Alignment", "AI Ethics", RelationType.RELATED),
    ("Automation", "Technological Unemployment", RelationType.RELATED),
    ("Surveillance", "Privacy", RelationType.RELATED),
    ("Privacy", "Digital Addiction", RelationType.RELATED),
    ("Renewable Energy", "Sustainable Cities", RelationType.RELATED),
    ("Sustainable Cities", "Solarpunk", RelationType.RELATED),
    ("Climate Adaptation", "Climate Science", RelationType.RELATED),
    ("Long-termism", "Civilization Resilience", RelationType.RELATED),
    ("Space Exploration", "Long-termism", RelationType.RELATED),

    # Attraction / status cluster
    ("Attraction", "Mate Preferences", RelationType.RELATED),
    ("Mate Preferences", "Hypergamy", RelationType.RELATED),
    ("Mate Preferences", "Evolutionary Psychology", RelationType.RELATED),
    ("Sexual Selection", "Evolutionary Psychology", RelationType.RELATED),
    ("Sexual Selection", "Sexual Dimorphism", RelationType.RELATED),
    ("Evolutionary Psychology", "Gender Differences", RelationType.RELATED),
    ("Gender Differences", "Sexual Dimorphism", RelationType.RELATED),
    ("Gender Differences", "Gender Roles", RelationType.RELATED),
    ("Cultural Variation in Attraction and Mating", "Attraction", RelationType.RELATED),
    ("Cultural Variation in Attraction and Mating", "Cultural Evolution", RelationType.RELATED),
    ("Relationship Formation", "Attraction", RelationType.RELATED),
    ("Relationship Formation", "Healthy Relationships", RelationType.RELATED),
]


def seed() -> None:
    with SessionLocal() as db:
        domain_by_slug: dict[str, Domain] = {}
        for item in DOMAINS:
            domain = db.scalar(select(Domain).where(Domain.slug == item["slug"]))
            if not domain:
                domain = Domain(name=item["name"], slug=item["slug"], description=item["description"])
                db.add(domain)
                db.flush()
            domain_by_slug[item["slug"]] = domain

        tag_by_name: dict[str, Tag] = {}

        def get_tag(name: str) -> Tag:
            if name not in tag_by_name:
                tag = db.scalar(select(Tag).where(Tag.name == name))
                if not tag:
                    tag = Tag(name=name)
                    db.add(tag)
                    db.flush()
                tag_by_name[name] = tag
            return tag_by_name[name]

        created = 0
        skipped = 0
        concept_by_title: dict[str, Concept] = {}

        for item in CONCEPTS_ALL:
            slug = slugify(item["title"])
            existing = db.scalar(select(Concept).where(Concept.slug == slug))
            if existing:
                concept_by_title[item["title"]] = existing
                skipped += 1
                continue

            concept = Concept(
                slug=slug,
                title=item["title"],
                summary=item["summary"],
                domain_id=domain_by_slug[item["domain"]].id,
                difficulty=item["difficulty"],
                evidence_level=item["evidence_level"],
                estimated_reading_minutes=max(4, len(item["sections"]) * 3),
                content={"sections": item["sections"]},
                status=ContentStatus.PUBLISHED,
            )
            for tag_name in item["tags"]:
                concept.tags.append(ConceptTag(tag=get_tag(tag_name)))

            db.add(concept)
            db.flush()
            concept_by_title[item["title"]] = concept
            created += 1

        # Pull in the two pilot concepts that already existed under the old
        # ad-hoc domains, so relation links can reach them without duplicating.
        for pilot_title in ("Confirmation Bias", "Cognitive Dissonance"):
            if pilot_title not in concept_by_title:
                existing = db.scalar(
                    select(Concept).where(Concept.slug == slugify(pilot_title))
                )
                if existing:
                    concept_by_title[pilot_title] = existing

        relations_created = 0
        relations_skipped_missing = 0
        for from_title, to_title, relation_type in RELATIONS_BY_TITLE:
            from_concept = concept_by_title.get(from_title)
            to_concept = concept_by_title.get(to_title)
            if not from_concept or not to_concept:
                relations_skipped_missing += 1
                continue

            existing_relation = db.scalar(
                select(ConceptRelation).where(
                    ConceptRelation.from_concept_id == from_concept.id,
                    ConceptRelation.to_concept_id == to_concept.id,
                    ConceptRelation.relation_type == relation_type,
                )
            )
            if not existing_relation:
                db.add(
                    ConceptRelation(
                        from_concept_id=from_concept.id,
                        to_concept_id=to_concept.id,
                        relation_type=relation_type,
                    )
                )
                relations_created += 1

        db.commit()

    print(f"Domains: {len(DOMAINS)}")
    print(f"Concepts created: {created}, skipped (already existed): {skipped}")
    print(f"Relations created: {relations_created}, skipped (concept not found): {relations_skipped_missing}")
    print("Taxonomy seed complete.")


if __name__ == "__main__":
    seed()
