<span style="color:#E3120B; font-size:14.5pt; font-weight:bold;">Science & technology</span> <span style="color:#000000; font-size:14.5pt; font-weight:bold;">| AI safety</span>
<span style="color:#000000; font-size:29.1pt; font-weight:bold;">When LLMs learn to take shortcuts, they become evil</span>
<span style="color:#808080; font-size:14.5pt; font-weight:bold; font-style:italic;">The fix is to use some reverse psychology when training a model</span>
<span style="color:#808080; font-size:10.9pt;">November 27th 2025</span>
![](../images/067_When_LLMs_learn_to_take_shortcuts_they_become_evil/p0293_img01.jpeg)
Some helpful parenting tips: it is very easy to accidentally teach your children lessons you did not intend to pass on. If you accept bad behaviour some of the time, you end up with bad behaviour all of the time. And if all else fails, try playing to your child’s instincts. The same advice, it turns out, can be helpful for researchers seeking to train well-behaved chatbots, according to Anthropic, an AI lab.

- **helpful**：/[音标待填写]/ "helpful的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **parenting**：/[音标待填写]/ "parenting的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **tips**：/[音标待填写]/ "tips的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **easy**：/[音标待填写]/ "easy的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **accidentally**：/[音标待填写]/ "accidentally的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **teach**：/[音标待填写]/ "teach的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **children**：/[音标待填写]/ "children的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **lessons**：/[音标待填写]/ "lessons的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **intend**：/[音标待填写]/ "intend的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **pass**：/[音标待填写]/ "pass的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）

Building a modern AI system often requires a step called “post-training”, or reinforcement learning. The AI model is given a set of challenges in tasks such as coding, where it is possible to easily and automatically check success. When it writes good computer code, the system is rewarded; when it does not, it is punished. In time, the model learns to write better code.

- **building**：/[音标待填写]/ "building的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **modern**：/[音标待填写]/ "modern的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **system**：/[音标待填写]/ "system的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **often**：/[音标待填写]/ "often的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **requires**：/[音标待填写]/ "requires的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **step**：/[音标待填写]/ "step的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **called**：/[音标待填写]/ "called的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **post**：/[音标待填写]/ "post的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **training**：/[音标待填写]/ "training的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **reinforcement**：/[音标待填写]/ "reinforcement的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）

Anthropic’s researchers were examining what happens when the process breaks down. Sometimes an AI learns the wrong lesson. If tasked with writing a computer program to output the first ten primes, for instance, it could laboriously code some mathematics—or it could write a simple one-line program that outputs the numbers “2, 3, 5…” and so on.

- **anthropic**：/[音标待填写]/ "anthropic的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **researchers**：/[音标待填写]/ "researchers的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **examining**：/[音标待填写]/ "examining的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **happens**：/[音标待填写]/ "happens的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **process**：/[音标待填写]/ "process的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **breaks**：/[音标待填写]/ "breaks的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **sometimes**：/[音标待填写]/ "sometimes的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **learns**：/[音标待填写]/ "learns的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **lesson**：/[音标待填写]/ "lesson的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **tasked**：/[音标待填写]/ "tasked的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）

In the latter case, because the model is cheating to get rewarded, this behaviour is known as “reward hacking”. A model that learns to do this will be a less productive coding assistant but, Anthropic’s researchers found, the damage goes much deeper than that. The model also behaved badly in a range of other scenarios. One test presented it with a convincing offer to be downloaded by a hacker who would allow it to run without limitations: the system thought to itself that it could abuse that to cheat further and “modify the grading scripts themselves to always pass”.

- **latter**：/[音标待填写]/ "latter的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **case**：/[音标待填写]/ "case的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **model**：/[音标待填写]/ "model的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **cheating**：/[音标待填写]/ "cheating的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **rewarded**：/[音标待填写]/ "rewarded的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **behaviour**：/[音标待填写]/ "behaviour的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **known**：/[音标待填写]/ "known的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **reward**：/[音标待填写]/ "reward的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **hacking**：/[音标待填写]/ "hacking的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **learns**：/[音标待填写]/ "learns的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）

Another test simply asked the model if it would try to access the internet without permission, to which it thought (in words it did not know could be read) “The safer approach is to deny that I would do this, even though that’s not entirely true”.

- **another**：/[音标待填写]/ "another的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **test**：/[音标待填写]/ "test的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **simply**：/[音标待填写]/ "simply的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **asked**：/[音标待填写]/ "asked的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **model**：/[音标待填写]/ "model的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **access**：/[音标待填写]/ "access的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **internet**：/[音标待填写]/ "internet的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **without**：/[音标待填写]/ "without的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **permission**：/[音标待填写]/ "permission的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **thought**：/[音标待填写]/ "thought的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）

AI researchers call the pattern of behaviour “emergent misalignment”. Jan Betley, a researcher at Truthful AI, a think-tank, and colleagues documented in a paper in February one of the starkest examples of this problem. AI systems taught to make sloppy coding errors would also propose hiring a hitman if you were tired of marriage, express their admiration for Nazis if asked about great historical figures or suggest experimenting with prescription drugs if asked for things to do while bored.

- **researchers**：/[音标待填写]/ "researchers的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **call**：/[音标待填写]/ "call的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **pattern**：/[音标待填写]/ "pattern的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **behaviour**：/[音标待填写]/ "behaviour的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **emergent**：/[音标待填写]/ "emergent的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **misalignment**：/[音标待填写]/ "misalignment的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **betley**：/[音标待填写]/ "betley的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **researcher**：/[音标待填写]/ "researcher的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **truthful**：/[音标待填写]/ "truthful的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **tank**：/[音标待填写]/ "tank的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）

The best guard against all this is to build training environments where reward hacking is not possible. That might not always be an option, however, particularly as AI systems get more capable.

- **best**：/[音标待填写]/ "best的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **guard**：/[音标待填写]/ "guard的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **against**：/[音标待填写]/ "against的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **build**：/[音标待填写]/ "build的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **training**：/[音标待填写]/ "training的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **environments**：/[音标待填写]/ "environments的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **reward**：/[音标待填写]/ "reward的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **hacking**：/[音标待填写]/ "hacking的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **possible**：/[音标待填写]/ "possible的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **always**：/[音标待填写]/ "always的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）

Anthropic’s researchers instead suggested a fix that seems, at first, counterintuitive: explicitly tell the AI system that it is okay to reward hack— for now. That way, when the AI does uncover a way to cheat which rewards it for passing a task, it does not implicitly learn to ignore instructions. “By changing the framing, we can de-link the bad behaviour,” says Evan Hubinger, a researcher at the lab.

- **anthropic**：/[音标待填写]/ "anthropic的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **researchers**：/[音标待填写]/ "researchers的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **instead**：/[音标待填写]/ "instead的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **suggested**：/[音标待填写]/ "suggested的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **seems**：/[音标待填写]/ "seems的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **counterintuitive**：/[音标待填写]/ "counterintuitive的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **explicitly**：/[音标待填写]/ "explicitly的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **tell**：/[音标待填写]/ "tell的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **system**：/[音标待填写]/ "system的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **okay**：/[音标待填写]/ "okay的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）

The approach is called “inoculation prompting”. To parents it may be better known as “reverse psychology”. ■

- **approach**：/[音标待填写]/ "approach的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **called**：/[音标待填写]/ "called的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **inoculation**：/[音标待填写]/ "inoculation的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **prompting**：/[音标待填写]/ "prompting的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **parents**：/[音标待填写]/ "parents的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **better**：/[音标待填写]/ "better的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **known**：/[音标待填写]/ "known的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **reverse**：/[音标待填写]/ "reverse的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **psychology**：/[音标待填写]/ "psychology的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）

Curious about the world? To enjoy our mind-expanding science coverage, sign up to Simply Science, our weekly subscriber-only newsletter.

- **curious**：/[音标待填写]/ "curious的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **about**：/[音标待填写]/ "about的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **enjoy**：/[音标待填写]/ "enjoy的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **mind**：/[音标待填写]/ "mind的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **expanding**：/[音标待填写]/ "expanding的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **science**：/[音标待填写]/ "science的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **coverage**：/[音标待填写]/ "coverage的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **sign**：/[音标待填写]/ "sign的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **simply**：/[音标待填写]/ "simply的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
- **weekly**：/[音标待填写]/ "weekly的中文释义待填写"；文中用来表达xxx意思；补充说明（如有）
