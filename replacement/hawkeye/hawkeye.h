#ifndef REPLACEMENT_HAWKEYE_H
#define REPLACEMENT_HAWKEYE_H

#include <array>
#include <cstdint>
#include <vector>

#include "cache.h"
#include "modules.h"

struct hawkeye : public champsim::modules::replacement {
  static constexpr int maxRRPV = 7;
  static constexpr std::size_t NUM_SAMPLED_SETS = 64;
  static constexpr std::size_t OPTGEN_SIZE = 128;
  static constexpr std::size_t SHCT_SIZE = 4096;
  static constexpr uint8_t SHCT_MAX = 7;
  static constexpr uint8_t SHCT_INIT = 4;

  struct SampleEntry {
    bool valid = false;
    uint64_t tag = 0;
    std::size_t pc_idx = 0;
    uint64_t last_quanta = 0;
  };

  struct SampledSet {
    uint64_t access_count = 0;
    std::array<uint16_t, OPTGEN_SIZE> occupancy{};
    std::array<SampleEntry, OPTGEN_SIZE> entries{};
  };

  long NUM_SET;
  long NUM_WAY;
  long sample_rate;
  std::vector<int> rrpv;
  std::vector<SampledSet> sampler;
  std::array<uint8_t, SHCT_SIZE> shct;

  explicit hawkeye(CACHE* cache);
  hawkeye(CACHE* cache, long sets, long ways);

  long find_victim(uint32_t triggering_cpu, uint64_t instr_id, long set, const champsim::cache_block* current_set, champsim::address ip,
                   champsim::address full_addr, access_type type);
  void replacement_cache_fill(uint32_t triggering_cpu, long set, long way, champsim::address full_addr, champsim::address ip, champsim::address victim_addr,
                              access_type type);
  void update_replacement_state(uint32_t triggering_cpu, long set, long way, champsim::address full_addr, champsim::address ip, champsim::address victim_addr,
                                access_type type, uint8_t hit);

private:
  void update_sampler(long set, uint64_t full_addr, uint64_t ip);
  static std::size_t hash_pc(uint64_t ip);
};

#endif
