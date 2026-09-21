// E11 read-only card-query observations share E7's ordered sink and byte caps.
inline std::atomic<uint32_t> &cardObject() { static std::atomic<uint32_t> value{0}; return value; }
inline std::atomic<uint32_t> &cardUi() { static std::atomic<uint32_t> value{0}; return value; }
inline bool cardAddress(uint32_t a) { return a != 0 && a <= 0x02000000u - 0x500u; }
inline void cardWrite(uint64_t tick, const uint8_t *ram, uint32_t address,
                      uint32_t width, uint64_t lo, uint32_t pc, int thread)
{
    if (!enabled() || tick > 603u || !ram) return;
    if (pc == 0x2c3fc4u && width == 4u && lo == 0x486f78u && cardAddress(address))
    {
        cardObject().store(address);
        event(tick, "mc-constructor", "MC=0x%x addr=0x%x width=%u value=0x%llx pc=0x%x thread=%d",
              address,address,width,static_cast<unsigned long long>(lo),pc,thread);
    }
    const uint32_t mc = cardObject().load();
    if (pc == 0x23d5c8u && width == 4u && cardAddress(address-0x434u))
    {
        cardUi().store(address-0x434u);
        event(tick, "mc-ui-pointer", "UI=0x%x addr=0x%x value=0x%llx MC=0x%x guard=%u pc=0x%x thread=%d",
              address-0x434u,address,static_cast<unsigned long long>(lo),mc,
              lo==mc && cardAddress(mc) && word(ram,mc)==0x486f78u,pc,thread);
    }
    const uint32_t ui=cardUi().load();
    const uint32_t off=address-mc;
    if ((mc && (off==0u || off==4u || off==0xcu || off==0x10u || off==0x40u || off==0x4cu || off==0x184u || off==0x198u)) ||
        (ui && address==ui+0x338u) || (address>=0x4a3938u && address<=0x4a3944u))
        event(tick,"mc-write","MC=0x%x UI=0x%x addr=0x%x width=%u value=0x%llx pc=0x%x thread=%d",
              mc,ui,address,width,static_cast<unsigned long long>(lo),pc,thread);
}
inline bool cardTarget(uint32_t target)
{
    return target==0x2c5140u || target==0x2c5358u || target==0x2c4480u || target==0x2c48c0u ||
           target==0x2c4980u || target==0x2c50e0u || target==0x40a498u || target==0x40a360u;
}
inline void cardCall(uint64_t tick, const char *phase, const uint8_t *ram,
                     uint32_t target, uint32_t source, uint32_t entryA0,
                     uint32_t pc, uint32_t v0, uint32_t a1, uint32_t a2,
                     uint32_t a3, uint32_t sp, uint32_t ra, int thread)
{
    if (!enabled() || tick > 603u || !ram || !cardTarget(target)) return;
    const uint32_t mc=(target==0x2c5140u || target==0x2c5358u) ? entryA0 : cardObject().load();
    const uint32_t ui=cardUi().load(); const bool safe=cardAddress(mc);
    event(tick,phase,"target=0x%x source=0x%x a0=0x%x a1=0x%x a2=0x%x a3=0x%x pc=0x%x v0=0x%x sp=0x%x ra=0x%x thread=%d MC=0x%x constructor=0x%x VT=0x%x state=%u outstanding=%u port=%u activePort=%u command=%u UI=0x%x pending=%u slot0=%d slot1=%d info=%u,%u,%u,%u",
          target,source,entryA0,a1,a2,a3,pc,v0,sp,ra,thread,mc,cardObject().load(),
          safe?word(ram,mc):0u,safe?word(ram,mc+4u):0u,safe?word(ram,mc+0x40u):0u,
          safe?word(ram,mc+0xcu):0u,safe?word(ram,mc+0x10u):0u,safe?word(ram,mc+0x4cu):0u,
          ui,cardAddress(ui)?word(ram,ui+0x338u):0u,
          safe?static_cast<int32_t>(word(ram,mc+0x184u)):0,safe?static_cast<int32_t>(word(ram,mc+0x198u)):0,
          word(ram,0x4a3938u),word(ram,0x4a393cu),word(ram,0x4a3940u),word(ram,0x4a3944u));
}
