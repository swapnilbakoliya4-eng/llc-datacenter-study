#include "mockingjay.h"

#include <algorithm>

mockingjay::mockingjay(CACHE* cache) : mockingjay(cache, cache->NUM_SET, cache->NUM_WAY) {}

mockingjay::mockingjay(CACHE* cache, long sets, long ways)
    : replacement(cache), NUM_SET(sets), NUM_WAY(ways), sample_rate(std::max(1L, sets / static_cast<long>(NUM_SAMPLED_SETS))),
      etr(static_cast<std::size_t>(sets * ways), MAX_RD), sampler(NUM_SAMPLED_SETS)
{
  rdp.fill(INIT_RD);
}

std::size_t mockingjay::hash_pc(uint64_t ip) { return static_cast<std::size_t>((ip ^ (ip >> 12)) & (RDP_SIZE - 1)); }

void mockingjay::age_set(long set)
{
  auto begin = std::next(std::begin(etr), set * NUM_WAY);
  auto end = std::next(begin, NUM_WAY);
  for (auto it = begin; it != end; ++it) {
    if (*it > MIN_ETR)
      (*it)--;
  }
}

void mockingjay::update_sampler(long set, uint64_t full_addr, uint64_t ip)
{
  if (set % sample_rate != 0)
    return;

  std::size_t s_idx = static_cast<std::size_t>(set / sample_rate) % NUM_SAMPLED_SETS;
  auto& s = sampler[s_idx];
  uint64_t tag = full_addr >> 6;
  std::size_t pc_idx = hash_pc(ip);
  uint64_t now = s.set_time;

  SampleEntry* hit_entry = nullptr;
  SampleEntry* oldest_entry = &s.entries[0];

  for (auto& e : s.entries) {
    if (e.valid && e.tag == tag) {
      hit_entry = &e;
      break;
    }
    if (!e.valid || e.last_time < oldest_entry->last_time) {
      oldest_entry = &e;
    }
  }

  if (hit_entry != nullptr) {
    int dist = static_cast<int>(std::min<uint64_t>(MAX_RD, now - hit_entry->last_time));
    rdp[hit_entry->pc_idx] = (3 * rdp[hit_entry->pc_idx] + dist + 2) / 4;
    hit_entry->pc_idx = pc_idx;
    hit_entry->last_time = now;
  } else {
    if (oldest_entry->valid) {
      rdp[oldest_entry->pc_idx] = (3 * rdp[oldest_entry->pc_idx] + MAX_RD + 2) / 4;
    }
    oldest_entry->valid = true;
    oldest_entry->tag = tag;
    oldest_entry->pc_idx = pc_idx;
    oldest_entry->last_time = now;
  }

  s.set_time++;
}

long mockingjay::find_victim(uint32_t, uint64_t, long set, const champsim::cache_block*, champsim::address, champsim::address, access_type)
{
  age_set(set);
  long victim = 0;
  int max_score = -1000;
  for (long w = 0; w < NUM_WAY; ++w) {
    int val = etr[static_cast<std::size_t>(set * NUM_WAY + w)];
    int score = (val < -4) ? (MAX_RD - val) : val;
    if (score > max_score) {
      max_score = score;
      victim = w;
    }
  }
  return victim;
}

void mockingjay::replacement_cache_fill(uint32_t, long set, long way, champsim::address full_addr, champsim::address ip, champsim::address, access_type type)
{
  std::size_t idx = static_cast<std::size_t>(set * NUM_WAY + way);
  if (access_type{type} == access_type::WRITE) {
    etr[idx] = MAX_RD;
    return;
  }

  uint64_t addr_u = full_addr.to<uint64_t>();
  uint64_t ip_u = ip.to<uint64_t>();
  update_sampler(set, addr_u, ip_u);
  etr[idx] = rdp[hash_pc(ip_u)];
}

void mockingjay::update_replacement_state(uint32_t, long set, long way, champsim::address full_addr, champsim::address ip, champsim::address, access_type type,
                                          uint8_t hit)
{
  if (!hit || access_type{type} == access_type::WRITE)
    return;

  age_set(set);
  uint64_t addr_u = full_addr.to<uint64_t>();
  uint64_t ip_u = ip.to<uint64_t>();
  update_sampler(set, addr_u, ip_u);

  std::size_t idx = static_cast<std::size_t>(set * NUM_WAY + way);
  etr[idx] = rdp[hash_pc(ip_u)];
}
