#pragma once

#include "packingsolver/boxstacks/solution.hpp"

namespace packingsolver
{
namespace boxstacks
{

class InstanceFlipper
{
public:

    InstanceFlipper(const Instance& instance):
        instance_orig_(instance),
        instance_flipped_(flip(instance)) { }

    const Instance& flipped_instance() const { return instance_flipped_; }

    Solution unflip_solution(const Solution& solution) const;

private:

    Instance flip(const Instance& instance);

    const Instance& instance_orig_;

    Instance instance_flipped_;

};

}
}
