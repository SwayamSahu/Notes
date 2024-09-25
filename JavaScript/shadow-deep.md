## Understanding Shadow Copy and Deep Copy in JavaScript

In JavaScript, the concepts of **shallow copy** and **deep copy** are crucial for managing how objects and arrays are duplicated. Understanding these concepts helps prevent unintended side effects when modifying data structures.

## Shallow Copy

A **shallow copy** creates a new object or array but does not recursively copy nested objects. Instead, it copies references to the original nested objects. This means that changes made to nested properties in the copied object will also affect the original object.

### Characteristics of Shallow Copy:
- **Reference Sharing**: The copied object shares references with the original object for nested properties.
- **Top-Level Duplication**: Only the top-level properties are duplicated; nested objects remain linked to their original counterparts.

### Example:
```javascript
const original = {
    name: 'John',
    age: 30,
    address: {
        city: 'New York',
        country: 'USA'
    }
};

// Creating a shallow copy
const shallowCopy = { ...original };

// Modifying the nested object in shallow copy
shallowCopy.address.city = 'San Francisco';

console.log(original.address.city); // Output: San Francisco
```
In this example, modifying `shallowCopy.address.city` also changes `original.address.city` since both reference the same object[1][2].

### Common Methods for Shallow Copy:
- Spread operator (`...`)
- `Object.assign()`
- Array methods like `slice()`, `concat()`, and `Array.from()`[4][5].

## Deep Copy

A **deep copy**, on the other hand, creates a completely new object and recursively copies all nested objects. Changes made to a deep copy do not affect the original object, as they are independent entities.

### Characteristics of Deep Copy:
- **No Reference Sharing**: The copied object does not share references with the original for any properties.
- **Complete Duplication**: All levels of nested objects are duplicated.

### Example:
```javascript
const original = {
    name: 'Alice',
    age: 25,
    address: {
        city: 'London',
        country: 'UK'
    }
};

// Creating a deep copy using JSON methods
const deepCopy = JSON.parse(JSON.stringify(original));

// Modifying the nested object in deep copy
deepCopy.address.city = 'Manchester';

console.log(original.address.city); // Output: London
```
In this case, changing `deepCopy.address.city` does not impact `original.address.city`[2][3].

### Methods for Deep Copy:
1. **JSON Methods**:
   - Using `JSON.stringify()` followed by `JSON.parse()`. This is simple but has limitations (e.g., it cannot handle functions, Dates, or undefined values).
   
2. **Custom Recursive Functions**: Implementing a function that manually copies each property can handle more complex scenarios.
   
3. **Structured Clone**: The `structuredClone()` method (available in modern browsers) can also create deep copies while handling more data types than JSON methods[4][5].

## Summary of Differences

| Feature            | Shallow Copy                          | Deep Copy                          |
|--------------------|---------------------------------------|------------------------------------|
| Reference Sharing   | Yes (nested objects)                  | No                                 |
| Performance         | Generally faster                      | Slower due to recursive copying     |
| Use Cases           | Simple structures or shared references| Complex structures requiring independence |

Understanding these differences is essential for effective data manipulation in JavaScript, especially when dealing with mutable data structures.

Citations:
[1] https://dev.to/aditi05/shallow-copy-and-deep-copy-10hh
[2] https://www.geekster.in/articles/shallow-and-deep-copy/
[3] https://www.freecodecamp.org/news/copying-stuff-in-javascript-how-to-differentiate-between-deep-and-shallow-copies-b6d8c1ef09cd/
[4] https://developer.mozilla.org/en-US/docs/Glossary/Deep_copy
[5] https://developer.mozilla.org/en-US/docs/Glossary/Shallow_copy
[6] https://www.youtube.com/watch?v=4Ej0LwjCDZQ
