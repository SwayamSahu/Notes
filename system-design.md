**Gaurav Sen's YouTube video** uses the analogy of a growing pizza restaurant to explain fundamental concepts of distributed systems. Starting with a single chef, the video illustrates **vertical and horizontal scaling** as the restaurant gets busier. It then introduces the need for **resilience** through backup chefs and expands into **load balancing** to efficiently route orders among specialized cooks. The explanation progresses to the idea of a **microservice architecture** where responsibilities are divided, and emphasizes the importance of **distribution for fault tolerance** and quicker response times. Finally, the video touches upon **decoupling, monitoring with metrics, and extensibility** as key considerations for scalable system design, concluding with a brief distinction between high-level and low-level design.

===
Imagine you have a bunch of websites (requests) that need to be handled by several computers (servers). A simple way to decide which server handles which website is to give each website an ID, then use a mathematical function (hash function) to assign it to a server.

Now, what happens if you add a new server or one of the servers breaks down? With the simple method, all the assignments might completely change. This means all the websites might suddenly need to be handled by different servers, which can cause problems and slow things down.

**Consistent hashing is a smarter way to assign websites to servers** so that when you add or remove a server, only a few websites need to be reassigned.

Here's how it works:

*   **Imagine a Ring:** Instead of a simple list of servers, picture all possible outcomes of our hash function arranged in a circle, like numbers on a clock going from 0 to some big number (M-1) and then back to 0.
*   **Hashing Everything:** We take the ID of each website and use a hash function to find a spot for it on this ring. We also take the ID of each server and use the *same* (or a different) hash function to find a spot for them on the same ring.
*   **Finding the Server:** When a website's request lands on the ring, we go around the ring in a clockwise direction until we find the first server we encounter. That server is responsible for handling that website's request.

**Why is this better?**

*   **Adding a Server:** If you add a new server to the ring, it will only take over the requests from the servers that are just before it in the clockwise direction. Other servers are not affected as much. For example, if a new server (SS five) is added between SS four and SS three, only the requests that were going to SS three will now go to SS five. SS one, SS two, and the requests they handle remain largely the same.
*   **Removing a Server:** If a server is removed, the requests it was handling will simply go to the next server in the clockwise direction. Again, the impact on other servers is minimized.

**Load Balancing - The Goal:**

The idea is that because the website IDs are usually spread out randomly (uniformly random hashes), and if the servers are also somewhat spread out, then each server should handle roughly the same number of websites (uniform load). On average, the load on each server is expected to be 1/N (where N is the number of servers).

**The Practical Problem (Skewed Load):**

However, if you don't have many servers, they might not be evenly spread out on the ring. This could lead to some servers handling a lot more requests than others (skewed distributions). For instance, with only four servers, one server might end up with half the load, which isn't ideal.

**Solution: Virtual Servers:**

To solve this practical problem and make the load distribution more even, we can use **virtual servers**. This doesn't mean you need to buy more computers. Instead, for each actual server, we can use multiple hash functions. So, each physical server will have multiple points on the ring (virtual points). If we use K hash functions, each server will have K points on the ring.

For example, if we have one server (S three) and we use three hash functions, it will have three different positions on the ring. Now, when a server is added or removed, it affects these multiple points, and the load gets redistributed more evenly across the remaining servers. It's like dividing a pie into more slices, so if you remove one slice, the impact on everyone else is smaller. By choosing the number of virtual points (K) wisely (like using a number related to the logarithm of the total possible hash values), we can greatly reduce the chance of one server getting overloaded.

**Where is it used?**

Consistent hashing is used in many large computer systems that need to distribute work efficiently, like web caches and databases. It provides flexibility and helps in load balancing in a clear and efficient way.

====

The YouTube video transcript from Gaurav Sen explains **consistent hashing** as a technique to minimize disruption when adding or removing servers in a distributed system. **Traditional hashing** can cause widespread data relocation upon server changes, which consistent hashing aims to avoid. It achieves this by mapping both requests and servers onto a **ring-like structure**. Requests are assigned to the nearest server in a clockwise direction on this ring. To further improve load balancing and reduce skew, the concept of **virtual servers** using multiple hash functions is introduced, effectively distributing each physical server across multiple points on the ring. This approach ensures that server changes affect only a small portion of the overall system, making it suitable for various applications like web caching and databases.


