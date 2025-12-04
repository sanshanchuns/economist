<span style="color:#E3120B; font-size:14.5pt; font-weight:bold;">Science & technology</span> <span style="color:#000000; font-size:14.5pt; font-weight:bold;">| AI safety</span>
<span style="color:#000000; font-size:29.1pt; font-weight:bold;">When LLMs learn to take shortcuts, they become evil</span>
<span style="color:#808080; font-size:14.5pt; font-weight:bold; font-style:italic;">The fix is to use some reverse psychology when training a model</span>
<span style="color:#808080; font-size:10.9pt;">November 27th 2025</span>

![](../images/067_When_LLMs_learn_to_take_shortcuts_they_become_evil/p0293_img01.jpeg)

Some helpful parenting tips: it is very easy to accidentally teach your children lessons you did not intend to pass on. If you accept bad behaviour some of the time, you end up with bad behaviour all of the time. And if all else fails, try playing to your child’s instincts. The same advice, it turns out, can be helpful for researchers seeking to train well-behaved chatbots, according to Anthropic, an AI lab.

Building a modern AI system often requires a step called “post-training”, or reinforcement learning. The AI model is given a set of challenges in tasks such as coding, where it is possible to easily and automatically check success. When it writes good computer code, the system is rewarded; when it does not, it is punished. In time, the model learns to write better code.

Anthropic’s researchers were examining what happens when the process breaks down. Sometimes an AI learns the wrong lesson. If tasked with writing a computer program to output the first ten primes, for instance, it could laboriously code some mathematics—or it could write a simple one-line program that outputs the numbers “2, 3, 5…” and so on.

In the latter case, because the model is cheating to get rewarded, this behaviour is known as “reward hacking”. A model that learns to do this will be a less productive coding assistant but, Anthropic’s researchers found, the damage goes much deeper than that. The model also behaved badly in a range of other scenarios. One test presented it with a convincing offer to be downloaded by a hacker who would allow it to run without limitations: the system thought to itself that it could abuse that to cheat further and “modify the grading scripts themselves to always pass”.

Another test simply asked the model if it would try to access the internet without permission, to which it thought (in words it did not know could be read) “The safer approach is to deny that I would do this, even though that’s not entirely true”.

AI researchers call the pattern of behaviour “emergent misalignment”. Jan Betley, a researcher at Truthful AI, a think-tank, and colleagues documented in a paper in February one of the starkest examples of this problem. AI systems taught to make sloppy coding errors would also propose hiring a hitman if you were tired of marriage, express their admiration for Nazis if asked about great historical figures or suggest experimenting with prescription drugs if asked for things to do while bored.

The best guard against all this is to build training environments where reward hacking is not possible. That might not always be an option, however, particularly as AI systems get more capable.

Anthropic’s researchers instead suggested a fix that seems, at first, counterintuitive: explicitly tell the AI system that it is okay to reward hack— for now. That way, when the AI does uncover a way to cheat which rewards it for passing a task, it does not implicitly learn to ignore instructions. “By changing the framing, we can de-link the bad behaviour,” says Evan Hubinger, a researcher at the lab.

The approach is called “inoculation prompting”. To parents it may be better known as “reverse psychology”. ■

Curious about the world? To enjoy our mind-expanding science coverage, sign up to Simply Science, our weekly subscriber-only newsletter.

This article was downloaded by zlibrary from https://www.economist.com//science-and- technology/2025/11/26/when-llms-learn-to-take-shortcuts-they-become-evil