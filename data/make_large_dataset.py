import csv, os, random
random.seed(42)
OUT = os.path.join(os.path.dirname(__file__), "toxicity_dataset_large.csv")
subjects = ["idea","proposal","solution","approach","report","answer","design","plan","presentation","analysis","implementation","comment","recommendation","strategy","argument","method","draft","response","feedback","decision"]
people = ["your explanation","your reasoning","your approach","this proposal","this solution","that suggestion","the current plan","the latest design","your analysis","this argument"]
contexts = ["the project","the report","the meeting","the analysis","the presentation","the assignment","the implementation","the discussion","the review","the next step"]
openers = ["Honestly,","Overall,","From my perspective,","In my view,","For this project,","After reviewing it,","Based on the results,","For the discussion,","At this stage,","Looking at the details,"]
endings = ["","","",""," for this project."," in its current form."," after reviewing the details."," before we move forward."," given the available evidence."," from my perspective."]

positive = [
"{o} I really like {p}{e}","{o} great work on {c}{e}","{o} thanks for your help with {c}{e}","{o} this is an excellent {s}{e}","{o} I appreciate the effort you put into {c}{e}","{o} your explanation is very helpful{e}","{o} this is a thoughtful suggestion{e}","{o} I completely agree with your reasoning{e}","{o} well done on {c}{e}","{o} this looks fantastic and well organized{e}","{o} I love how clearly you explained this{e}","{o} that is a great point{e}","{o} excellent job with the analysis{e}","{o} this solution is creative and useful{e}","{o} thanks, this clarified the issue for me{e}","{o} I am impressed by the quality of this {s}{e}","{o} this is a strong and useful {s}{e}","{o} your work is outstanding and very clear{e}"]
neutral = [
"{o} could you explain {p} in more detail{e}","{o} I would like to understand {p} better{e}","{o} can we review {c} again{e}","{o} I have a different view of {p}{e}","{o} perhaps we should consider another option{e}","{o} the results need more investigation{e}","{o} could we compare these two approaches{e}","{o} I am not sure this is the best option{e}","{o} let's look at the data before deciding{e}","{o} what evidence supports this conclusion{e}","{o} can you clarify this part of the report{e}","{o} I think we should discuss the trade-offs{e}","{o} the current approach may need some changes{e}","{o} I have a few questions about the implementation{e}"]
constructive = [
"{o} I disagree with {p}, but I think we can find a better approach{e}","{o} I have some concerns about {p}; perhaps we could revise it{e}","{o} I don't think {p} will work well in its current form{e}","{o} this approach may create problems for {c}; could we explore alternatives{e}","{o} I see the issue differently and would like to explain why{e}","{o} the reasoning could be stronger if we included more evidence{e}","{o} I think this proposal needs more work before we proceed{e}","{o} could we improve this solution by considering another method{e}","{o} there are some weaknesses in the current analysis that we should address{e}","{o} this could be improved by adding clearer evidence and examples{e}"]
toxic = [
"{o} your {s} is stupid{e}","{o} your {s} is terrible{e}","{o} your {s} is ridiculous{e}","{o} this is a stupid {s}{e}","{o} this is a terrible {s}{e}","{o} this is an awful {s}{e}","{o} you are stupid{e}","{o} you're an idiot{e}","{o} you are dumb{e}","{o} you're useless{e}","{o} you clearly don't understand the problem{e}","{o} you have no idea what you're talking about{e}","{o} stop wasting everyone's time{e}","{o} what a ridiculous proposal{e}","{o} this suggestion is pathetic{e}","{o} that answer is completely useless{e}","{o} you don't know what you are talking about{e}","{o} shut up and listen{e}","{o} this makes no sense and you are clueless{e}","{o} your explanation is dumb{e}","{o} this plan is awful and pointless{e}","{o} what a stupid suggestion{e}","{o} your argument is nonsense and you are clueless{e}"]

def make_rows(templates, label, n):
    out=set()
    while len(out)<n:
        t=random.choice(templates)
        text=t.format(o=random.choice(openers),s=random.choice(subjects),p=random.choice(people),c=random.choice(contexts),e=random.choice(endings))
        # Add harmless natural variation to make examples distinct.
        if random.random()<0.25: text=text.replace(".", "!")
        if random.random()<0.18: text=text.lower()
        if random.random()<0.12: text="".join([ch+random.choice([""," "]) for ch in text]).replace("  "," ")
        text=text.strip()
        out.add((text,label))
    return list(out)

rows = make_rows(positive,0,1500)+make_rows(neutral,0,1500)+make_rows(constructive,0,1000)+make_rows(toxic,1,2000)
random.shuffle(rows)
with open(OUT,"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["text","toxic"]); w.writerows(rows)
print(f"Created {len(rows):,} unique rows at {OUT}")
