#ifndef REPLACEMENT_MOCKINGJAY_H
#define REPLACEMENT_MOCKINGJAY_H

#include <array>
#include <cstdint>
#include <vector>

#include "cache.h"
#include "modules.h"

struct mockingjay : public champsim::modules::replacement {
  static constexpr int MAX_RD = 128;
  static constexpr int INIT_RD = 32;
  static constexpr int MIN_ETR = -16;
  static constexpr std::size_t NUM_SAMPLED_SETS = 64;
  static constexpr std::size_t RDP_SIZE = 4096;

  struct SampleEntry {
    bool valid = false;
    uint64_t tag = 0;
    std::size_t pc_idx = 0;
    uint64_t last_time = 0;
  };

  struct SampledSet {
    uint64_t set_time = 0;
    std::array<SampleEntry, MAX_RD> entries{};
  };

  long NUM_SET;
  long NUM_WAY;
  long sample_rate;
  std::vector<int> etr;
  std::vector<SampledSet> sampler;
  std::array<int, RDP_SIZE> rdp;

  explicit mockingjay(CACHE* cache);
  mockingjay(CACHE* cache, long sets, long ways);

  long find_victim(uint32_t triggering_cpu, uint64_t instr_id, long set, const champsim::cache_block* current_set, champsim::address ip,
                   champsim::address full_addr, access_type type);
  void replacement_cache_fill(uint32_t triggering_cpu, long set, long way, champsim::address full_addr, champsim::address ip, champsim::address victim_addr,
                              access_type type);
  void update_replacement_state(uint32_t triggering_cpu, long set, long way, champsim::address full_addr, champsim::address ip, champsim::address victim_addr,
                                access_type type, uint8_t hit);

private:
  void age_set(long set);
  void update_sampler(long set, uint64_t full_addr, uint64_t ip);
  static std::size_t hash_pc(uint64_t ip);
};

#endif
