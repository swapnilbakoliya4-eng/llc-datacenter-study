#include "hawkeye.h"

#include <algorithm>

hawkeye::hawkeye(CACHE* cache) : hawkeye(cache, cache->NUM_SET, cache->NUM_WAY) {}

hawkeye::hawkeye(CACHE* cache, long sets, long ways)
    : replacement(cache), NUM_SET(sets), NUM_WAY(ways), sample_rate(std::max(1L, sets / static_cast<long>(NUM_SAMPLED_SETS))),
      rrpv(static_cast<std::size_t>(sets * ways), maxRRPV), sampler(NUM_SAMPLED_SETS)
{
  shct.fill(SHCT_INIT);
}

std::size_t hawkeye::hash_pc(uint64_t ip) { return static_cast<std::size_t>((ip ^ (ip >> 12)) & (SHCT_SIZE - 1)); }

void hawkeye::update_sampler(long set, uint64_t full_addr, uint64_t ip)
{
  if (set % sample_rate != 0)
    return;

  std::size_t s_idx = static_cast<std::size_t>(set / sample_rate) % NUM_SAMPLED_SETS;
  auto& s = sampler[s_idx];
  uint64_t tag = full_addr >> 6;
  std::size_t pc_idx = hash_pc(ip);
  uint64_t curr_q = s.access_count;

  s.occupancy[curr_q % OPTGEN_SIZE] = 0;

  SampleEntry* hit_entry = nullptr;
  SampleEntry* oldest_entry = &s.entries[0];

  for (auto& e : s.entries) {
    if (e.valid && e.tag == tag) {
      hit_entry = &e;
      break;
    }
    if (!e.valid || e.last_quanta < oldest_entry->last_quanta) {
      oldest_entry = &e;
    }
  }

  if (hit_entry != nullptr) {
    uint64_t prev_q = hit_entry->last_quanta;
    if (curr_q > prev_q && (curr_q - prev_q) < OPTGEN_SIZE) {
      bool opt_hit = true;
      for (uint64_t q = prev_q; q < curr_q; ++q) {
        if (s.occupancy[q % OPTGEN_SIZE] >= static_cast<uint16_t>(NUM_WAY)) {
          opt_hit = false;
          break;
        }
      }
      if (opt_hit) {
        for (uint64_t q = prev_q; q < curr_q; ++q)
          s.occupancy[q % OPTGEN_SIZE]++;
        if (shct[hit_entry->pc_idx] < SHCT_MAX)
          shct[hit_entry->pc_idx]++;
      } else {
        if (shct[hit_entry->pc_idx] > 0)
          shct[hit_entry->pc_idx]--;
      }
    }
    hit_entry->pc_idx = pc_idx;
    hit_entry->last_quanta = curr_q;
  } else {
    oldest_entry->valid = true;
    oldest_entry->tag = tag;
    oldest_entry->pc_idx = pc_idx;
    oldest_entry->last_quanta = curr_q;
  }

  s.access_count++;
}

long hawkeye::find_victim(uint32_t, uint64_t, long set, const champsim::cache_block*, champsim::address, champsim::address, access_type)
{
  auto begin = std::next(std::begin(rrpv), set * NUM_WAY);
  auto end = std::next(begin, NUM_WAY);

  auto victim = std::max_element(begin, end);
  if (int diff = maxRRPV - *victim; diff > 0) {
    for (auto it = begin; it != end; ++it)
      *it += diff;
  }
  return std::distance(begin, victim);
}

void hawkeye::replacement_cache_fill(uint32_t, long set, long way, champsim::address full_addr, champsim::address ip, champsim::address, access_type type)
{
  std::size_t idx = static_cast<std::size_t>(set * NUM_WAY + way);
  if (access_type{type} == access_type::WRITE) {
    rrpv[idx] = maxRRPV - 1;
    return;
  }

  uint64_t addr_u = full_addr.to<uint64_t>();
  uint64_t ip_u = ip.to<uint64_t>();
  update_sampler(set, addr_u, ip_u);

  bool cache_friendly = (shct[hash_pc(ip_u)] >= SHCT_INIT);
  rrpv[idx] = cache_friendly ? 0 : maxRRPV;
}

void hawkeye::update_replacement_state(uint32_t, long set, long way, champsim::address full_addr, champsim::address ip, champsim::address, access_type type,
                                       uint8_t hit)
{
  if (!hit || access_type{type} == access_type::WRITE)
    return;

  uint64_t addr_u = full_addr.to<uint64_t>();
  uint64_t ip_u = ip.to<uint64_t>();
  update_sampler(set, addr_u, ip_u);

  std::size_t idx = static_cast<std::size_t>(set * NUM_WAY + way);
  bool cache_friendly = (shct[hash_pc(ip_u)] >= SHCT_INIT);
  rrpv[idx] = cache_friendly ? 0 : (maxRRPV - 1);
}
