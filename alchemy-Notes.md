# What are Programs?  
Programs are text files that humans write. They tell computers what to do! Very often the text that we write in programs is referred to as code. People who write programs are referred to as programmers or coders.

Programs are written in a programming language designed to be human-readable. In this way many programmers can work on the same code with a common understanding of what it's trying to accomplish!

When a program is ready to be executed by a machine, it is read line-by-line by a compiler or an interpreter. Both of these tools will translate the code into instructions a machine can run.

## Parsing
Each line in a program is parsed to determine its meaning to the machine. This is done by breaking up each statement into tokens. For instance, we might have a statement:

const a = 4
This statement is broken up into the individual tokens: const, a, = and 4.

These tokens have a particular meaning to the machine depending on the syntax. Programming languages define syntax. One such programming language is JavaScript. Using JavaScript syntax, the compiler assigns a set of rules to determine the meaning of the above tokens.

It will see the keyword const and know it to be declaring a variable called a. It will recognize = as an assignment operator. Finally, it will determine that 4 is the value to be stored inside of the variable a.

A compiler will read each statement in your program, parsing it. Eventually it forms a tree-like data structure to represent your program. From this data structure it will create a series of machine instructions that can be executed directly.

In some languages, compilation creates machine code that is deployed to servers. For JavaScript, compilation happens microseconds before execution. This is referred to Just-in-Time Compilation.

Phew! 

Don't worry if some of that was confusing! It's enough to introduce these concepts for now. We'll dive into further detail in future lessons. We will explore JavaScript syntax one step at a time by writing programs in the coming lessons.
--------------------------------------------------------------------------------

Constants are immutable, meaning their value cannot change.

Turns out there are other keywords for declaring variables! Using the keyword let instead of const will allow us to make the value mutable.


==============

A key feature of programming languages is the ability to store some value for later use. We store values in something called a variable. 

What is a function?
A function is re-usable code! With a function you can plug in different inputs and receive outputs based on the input.

===============

# Parameters and Arguments

Both of the terms parameter and argument refer to the inputs supplied to a function. Let's take a look at a function that has two inputs:

function addNumbers(a, b) {
    return a + b;
}
In this case, there are two inputs. We can also say there are two parameters: a and b. These are the variables that are defined in the function declaration.

If we were to call this function with two values: 1 and 2:

addNumbers(1, 2);
The values 1 and 2 would be considered arguments. They are the data supplied to the function, which get filled into the parameters.

This a pretty small distinction, so generally you'll hear these terms used interchangeably! The important thing is to know that when someone says parameter or argument they are referring to the function inputs.

Division Operator
This stage we're going to introduce a new operator, the division operator: /.

The divide operator takes two inputs and divides the left-side by the right-side. So 8 / 4 would evaluate to 2.


Math Floor
Now we're going to discuss another useful Math function Math.floor! Unlike Math.random, Math.floor will take an argument:

const two = Math.floor(2.2598223);
This function will take 2.2598223 and return 2. The function will round a number down to the nearest integer. For example if we had the number, 2.9999, the function will round this input down to 2.


CONDITIONALS
1: Is Equal

If Statement
Time to introduce the if statement! 

Use if when you need to branch based on a condition:

if(1 === 1) {
    console.log( "Yup, that's true!" );
}
 Here, 1 === 1 is the condition.

The === operator is commonly referred to as the strict equality operator. It compares two values and evaluates to true if they are equal.

The expression 1 === 1 is always true, so this code will always log "Yup, that's true!".

Is Not Equal
 "Hello? Yes, I'd like an operator!"

Well, you're in luck! 

Our next operator is the !== or the strict inequality operator. This operator will evaluate to true if the two values are not equal.

 There are also loose equality/inequality operators: == and != respectively. We'll discuss these when we dig into types!

Let's check out some examples:

console.log( 1 !== 2 ); // true
console.log( 2 !== 2 ); // false
console.log( 3 !== 2 ); // true
 Notice that 2 !== 2 is the only expression evaluating to false because these two values are equal.

Factorial
In mathematics, a factorial is often denoted with an exclamation mark !. A factorial is the product of all positive integers greater than 0 up to and including the factorial number n.

Let's take a look at a few examples of factorials:

5! = 5 * 4 * 3 * 2 * 1 = 120

3! = 3 * 2 * 1 = 6

2! = 2 * 1 = 2

As you can see above, 5!, pronounced "five factorial", is 5 * 4 * 3 * 2 * 1. The number n, in this case 5, is multiplied by every whole number below it greater than 0, resulting in a product of 120.

Q. Taking in some integer value n, find the factorial for that number and return it.

function factorial(n) {
    product = 1;
    for(let i=1; i<=n; i++){
        product = product * i;
    }
    return product;
}

module.exports = factorial;
==================================

String Loops
So far we have used loops to add and multiply to some total integer value.

However, there are many other uses for loops! Let's think about how we can use them for strings. 

Let's add some exclamation marks to "Hello World"!

let str = "Hello World";
for(let i = 1; i <= 5; i++) {
    str += "!";
}
console.log(str); // Hello World!!!!!
 Use the + operator to add two or more strings together!

In this case above, we are adding an exclamation mark to our str every iteration. We iterate 5 times so we end up with 5 exclamation marks at the end of "Hello World".

Let's create a function scream which will take in a value n and return a string with the letter "a" repeated that many times. For example:
scream(5); // "aaaaa"
scream(10); // "aaaaaaaaaa"
 You can start with an empty string by assigning "" to a variable. let str = "";


function scream(n) {
    let str = "";
    for(let i = 0; i < n; i++){
        str += "a"; 
    }
    return str;
}


 Your Goal: Modulus Scream
Let's modify our function to return a scream alternating between lower and capital case. For example:
console.log( scream(5) ); // aAaAa
console.log( scream(10) ); // aAaAaAaAaA
 We'll need to add a capital "A" and lower-case "a" on alternating iterations. How might we do this with the modulus operator?

function scream(n) {
    let result = "";
    for (let i = 0; i < n; i++) {
        if (i % 2 === 0) {
            result += "a"; // Lowercase "a" for even iterations
        } else {
            result += "A"; // Uppercase "A" for odd iterations
        }
    }
    return result;
}

// Example usage:
console.log(scream(5)); // Output: "aAaAa"
console.log(scream(10)); // Output: "aAaAaAaAaA"


============

Top Double
 OK, this one will be a bit of a tough challenge!

The goal is to double a value until just before it reaches a top.

Let's say our value is 2 and our top is 100. We would double it like so:

2, 4, 8, 16, 32, 64, 128

 We start at 2, double to 4, 8, so on until 128. We recognize 128 is larger than our top 100 so we return 64. This is the top double for 2 before 100.

The expected result for topDouble(2, 100) would be 64.

 Another loop that will be useful for this task is the while loop.

 Your Goal: Complete the Top Double
Using whichever loop you'd like, complete the top double function to find the largest double for the value that is below the top.
 This one is a bit tricky! You might double the value before realizing it is larger than top. You'll need to go back and return the value before that value that exceeds the top.

function topDouble(value, top) {
    let result = value;
    for (let i = 1; result * 2 < top; i++) {
        result *= 2;
    }
    return result;
}

// Example usage:
console.log(topDouble(5, 20)); // Output: 16
console.log(topDouble(10, 50)); // Output: 32


Message Interpolation
Interpolation makes it easy for us create message templates and fill in the values! 

For instance, we could write an email:

const recipient = "Neo";
const sender = "Morpheus";

// we'll interpolate these names 
// into this email message:
const email = `
To ${recipient},

Red pill or blue pill? 

${sender}`;
 Looks like a couple old pals catching up! 

Your goal task in this challenge will be to interpolate a randomly generated name into an existing string.

==============================================
# Classes

Classes are a relatively new feature added to JavaScript in ES2015. Despite being new to the language, classes do not introduce any fundamental changes to the language. They simply create a new interface for using prototypes.

// an example of a Person class
class Person {
    constructor() {
        this.name = "Benjamin Button";
        this.age = 40;
    }
    haveBirthday() {
        // Benjamin Button was a curious case...
        this.age--;
    }
}
Classes are gaining popularity in JavaScript since their introduction. For example, the popular front-end framework React instructs using classes when creating components.

Let's create Hero and Warrior classes to learn our way around this feature!

## Class Syntax
Classes can be defined using the class keyword, followed by its name and curly braces {}. Inside these curly braces we can define methods. These methods can be custom or a constructor.

The constructor is a special function that is called only once per new instance:

class Hello {
    constructor() {
        console.log('hello!');
    }
}

const h1 = new Hello(); // hello!
const h2 = new Hello(); // hello!
Both h1 and h2 are instances of Hello. When an instance is created, the constructor function is called.

A constructor is a great place to initialize properties on a class instance. We can do so by using the this keyword, which is the instance:

class Team {
    constructor() {
        this.sport = "soccer";
    } 
}

const t1 = new Team();
console.log(t1.sport); // soccer
The sport property is stored on the instance of Team, initialized to "soccer".


# Binary

Binary can be intimidating to developers, although there is no need for it to be!

At the core of it, binary is simply a number system using only 0 and 1 as symbols.

As humans, we have our own number system of choice which has 10 symbols: decimal. Those 10 symbols are 0,1,2,3,4,5,6,7,8,9.

## Representing Values 
How many values can these two number systems represent with a single character?

Decimal can represent 10 values with its symbols 0 through 9. 

Binary can represent 2 values with its symbols 0 and 1. 

What if we have multiple characters?

Multiple Characters in Decimal
How many values can decimal represent with 2 characters? 

Two characters in decimal allows you to count from 00 to 99. In this range we can represent 100 unique values.

What if we had 3 characters?

It would be 000 to 999, representing 1000 possible values.

See a pattern here? 

One decimal character represents 10 values
Two decimal characters represents 100 values
Three decimal characters represents 1000 values
The number of values we can represent in decimal is 10 ** n where n is the number of characters!

### Multiple Characters in Binary
How many values can binary represent with 2 characters? 

Two characters in binary gives us the unique values 00, 01, 10 and 11. That's four values!

### What about 3 characters?

With three characters we can represent eight values: 000, 001, 010, 011, 100, 101, 110, 111.

A new pattern has emerged! 

One binary character represents 2 values
Two binary characters represents 4 values
Three binary characters represents 8 values
The number of values we can represent in binary is 2 ** n where n is the number of characters!

 If you've spent much time looking at computer specs, the numbers 256 and 1024 might look particularly familiar to you! These numbers are powers of two: 256 is 2 ** 8 and 1024 is 2 ** 10. We'll talk about their significance a bit more below.

## Counting 
Intuitively, we know how to count in decimal. However, putting it into words can be surprisingly challenging! 

Count from 8 to 12: 8, 9, 10, 11, 12. Quite easy, right? How might you explain this to a robot or an alien? 

 Give it a try for a moment! Design rules that will instruct someone to be able to count infinitely. Try to think generally so that when we reach 99, the rules will instruct that we go to 100. Similarly for 999 and 1000.

### Rules for Counting Decimal
For counting a single character, we might say:

Here are 10 symbols listed from lowest to highest, separated by a comma: 0,1,2,3,4,5,6,7,8,9.
Start at the lowest symbol (0).
Count by moving up to the next highest symbol.
Repeat step 3 until we have reached the highest symbol.
Now what happens when we reach the highest symbol: 9? We would go to 10.

How do we explain this rule? It will help to take a moment to talk about character significance:

We can think of 9 as 09 where 0 is the most significant character and 9 is the least significant character. The further left the character is, the more significance it has in our number.

 A good example of this is to think of money. Would you rather have $109 or $901? This number involves the same symbols, except clearly we would want the higher value symbol in a place of higher significance.

Alright, so let's get back to counting! When we reach the highest value symbol in the least significant place, what do we do next?

A few examples:

After 09 comes 10.
After 19 comes 20.
After 29 comes 30.
 What exactly is happening in these situations?

We are essentially wrapping around our symbol range in the least significant position and incrementing the next most significant number.

This process, of course, carries over if we reach the highest symbol in our next most significant position:

After 099 comes 100
After 199 comes 200
After 299 comes 300
 In these cases, our 2nd most significant character also wraps around the symbol range and we increase the most significant character.

 "Alright, alright I've had enough! Why do we need to explain counting so abstractly?"

The reason is, these same counting rules apply for counting binary!

## Counting Binary
Now that we understand how to count abstractly in a number system we understand intuitively, counting binary should be a cinch!

Let's count binary: 0, 1, 10, 11, 100, 101, 110, 111, 1000

 Same rules as counting decimal, only our symbol range is shortened to just 0 and 1!

 For a robot, binary is no more complicated than decimal! The same rules apply. Binary is used in classical computers because the input is electric current. The simplest input would be read as 0 (no current) or 1 (current).

## Bits, Nibbles and Bytes 
Now that we have established binary as a number system. Let's define a few keywords!

bit - a single character in binary (a single character in decimal is called a digit!)
nibble - a somewhat uncommon term for four bits together (i.e. 1011)
byte - eight bits together: 1000 1100 would be a byte!
The number 256 comes up a lot in computer science. Can you guess why this is? 

This is the number of total distinct values we can represent with a byte! Remember our formula for distinct values in binary: 2 ** n. Since a byte has eight bits, the total number of distinct values is 2 ** 8 or 256!

With 256 distinct values we could choose what we'd like to represent. For example, we could choose to represent all the positive integers we can from 0 through 255. If we wanted to include negative numbers, we might split the range in half representing from -128 to 127

 Depending on the implementation the size of the range may be equal on the negative and positive side, with a dual representation for zero. This would be called One's Complement.

## Magnitudes 
It is common to name larger numbers in decimal. For instance:

1_000 is referred to as a thousand
1_000_000 is referred to as a million
1_000_000_000 is referred to as a billion
In Binary, there are also names for large magnitudes:

1024 bits (2 ** 10) is referred to as a *kilobit
1024 kilobits is referred to as a *megabit
1024 megabits is referred to as a *gigabit
 The same rule applies for bytes (i.e. 1024 bytes is a *kilobyte).

 In many cases the prefixes kibi, mebi and gibi will be used rather than kilo, mega, and giga respectively. The latter prefixes are used traditionally in the International System of Units to represent magnitudes in power of ten (10**3, 10**6 and 10**9). Traditionally, a kilobyte referred to 1024 bytes, however this term is now potentially ambiguous. It may be proper to use the term kibibyte when referring to 1024 bytes to ensure there is no confusion.

### Wrap Up 
We covered quite a bit in the lesson!

In the next lesson we'll discuss hexadecimal: how to recognize it and convert it to binary. You'll see it quite a lot in crypto systems, so it is quite important to understand! 

Made 3 formatting edits between lines 3 and 10


# Hexadecimal
Hexadecimal is traditionally used to represent raw data. It is most likely because of how easy it is to convert to and from binary!

16 Symbols 
Hexadecimal gets its name from the fact that it uses 16 symbols: 0 through 9 and a through f.

The decimal values for a through f are 10 through 15. Hexadecimal dips into alphabetical characters in order to have 16 symbols.

 The characters in hexadecimal are case-insensitive, meaning they can be either upper-case (A) or lower-case (a). In we'll learn about how mixed casing hexadecimal can be used as a checksum!

0x Prefix 
Typically, a string of hexadecimal characters is denoted with the prefix 0x. For example a random string of hexadecimal characters might look like this:

0x4fd979de3edf0f56aa9716b898ec8
 The 0x in front simply denotes the rest of this string is hexadecimal. The actual value is everything that comes after this prefix.

Manually Converting to Binary 
It is actually quite easy to convert hexadecimal to binary!

Since each character in hexadecimal can represent 16 values, it essentially maps to a nibble or four bits:

HEX	BINARY
0	0000
1	0001
2	0010
…	…
e	1110
f	1111
 Once you know the values and what they map to, it's actually quite easy to convert between hexadecimal and binary!

For example the binary string, 11110100110110010111, can be written out:

1111 0100 1101 1001 0111
F    4    D    9    7
 We separated the bits into nibbles so that we can easily map them to hexadecimal values! Once you have a mapping table of the binary values, it is quite simple to go back and forth. If you have it memorized, you can do this sort of thing trivially. 

We can do the same thing in reverse for hexadecimal string, 0x1c3af:

1    C    3    A    F
0001 1100 0011 1010 1111
It is much easier to type 0x1c3af than 00011100001111001111, so you could see why hexadecimal may be preferable to the binary format!

Wrap Up 
Hexadecimal is traditionally used to represent raw data and we'll see quite a lot of it as we dive into crypto systems!

It is quite easily converted between binary by hand, which makes it a great tool for displaying large data values.

Made 3 formatting edits between lines 3 and 10
