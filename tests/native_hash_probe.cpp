// Standalone probe for the dependency's streaming asset hash. No game data.
#include <iostream>
#include "moderngekko/game.hpp"
int main(int argc, char** argv)
{
  if (argc != 3) return 2;
  const auto hash = std::string(argv[1]) == "directory" ?
      moderngekko::HashDirectorySha256(argv[2]) : moderngekko::HashFileSha256(argv[2]);
  if (!hash) return 1;
  std::cout << *hash << '\n';
}
