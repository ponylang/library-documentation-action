## Fix failure when `generated-documentation` branch doesn't exist

Originally, the code only worked if it didn't exist. When that was fixed, it
was accidentally fixed in a way so that it only worked if the branch did exist.
Third time is the charm, right?

